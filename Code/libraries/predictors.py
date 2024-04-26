import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 
# Previous line is a patch to hide a warning about tensorflow not using AVX2 FMA instructions
# Full solution is here: https://technofob.com/2019/06/14/how-to-compile-tensorflow-2-0-with-avx2-fma-instructions-on-mac/

from   collections   import Counter
from   bitarray      import bitarray
from   abc           import ABC, abstractmethod
from   codes         import Huffman, Arithmetic
import tensorflow    as tf
import numpy         as np
from   tensorflow.keras.models import Sequential
from   tensorflow.keras.layers import LSTM, Input, Dense, Dropout
from   tensorflow.keras.utils  import to_categorical
import json, random


#############################################################


class Predictor(ABC):
  
  def __init__(self, data = None):
    if data is not None: self.train(data)
  
  @abstractmethod
  def train(self, text): pass
  
  @abstractmethod
  def frequencies_given_context(self, context, memoize=True): pass
  
  def surprisal(self, data, context=None):
    symbols       = []
    probabilities = []
    ranks         = []
    for index, symbol in enumerate(data):
      context             = self.context(data, index, context)
      symbol_frequencies  = self.frequencies_given_context(context)
      symbol_frequency    = symbol_frequencies[symbol]
      symbol_probability  = symbol_frequencies[symbol]/symbol_frequencies.total()
      symbol_rank = len([sym for sym,freq in symbol_frequencies.items() if freq>symbol_frequency])+1
      
      symbols.append(symbol)
      probabilities.append(symbol_probability)
      ranks.append(symbol_rank)
    return (symbols, probabilities, ranks)



#############################################################


class NGramPredictor(Predictor):

  def __init__(self, text, window = 6):
    self.window = window
    super().__init__(text)
  
  def context(self, text, index, previous_context=None):
    return bytes(text[index-self.window+1:index]) if index-self.window+1>=0 else b''
  
  def train(self, text):
    
    self.completions = {}
    
    for i in range(len(text)-self.window+1):
      stub = text[i:i+self.window-1]
      if stub in self.completions:
        self.completions[stub].update([text[i+self.window-1]])
      else: self.completions[stub] = Counter([text[i+self.window-1]])
    
    for stub in self.completions:
      for completion in self.completions[stub]:
        self.completions[stub][completion] *= 1000000
      self.completions[stub].update(bytes(range(256)))
    
    self.byte_counts = Counter(text)
    self.byte_counts.update(bytes(range(256)))
  
  def frequencies_given_context(self, context, memoize=True):
    return self.completions[context] if context in self.completions else self.byte_counts


#############################################################


class LSTMPredictor(Predictor):
  
  def __init__(self, basis_text, window):
    self.window = window
    self.model = self._build_model()
    if basis_text: self.train(basis_text)
    self.completions = {}
  
  def context(self, text, index, previous_context=None):
    return bytes(text[index-self.window:index]) if index-self.window>=0 else b''

  def _build_model(self):
    model = Sequential()
    model.add(Input(shape=(self.window,1)))
    model.add(LSTM(256))
    model.add(Dropout(0.2))
    model.add(Dense(256, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

  def train(self, data):

    seq_length = self.window
    dataX, dataY = [], []
    for i in range(len(data) - seq_length):
      seq_in = data[i:i + seq_length]
      seq_out = data[i + seq_length]
      dataX.append([byte for byte in seq_in])
      dataY.append(seq_out)

    X = np.reshape(dataX, (len(dataX), seq_length, 1)) / 255.0
    y = to_categorical(dataY, num_classes=256)

    self.model.fit(X, y, epochs=1, batch_size=2048)
  
  def frequencies_given_context(self, context, memoize=True):
    if context in self.completions:
      return self.completions[context]
    if len(context)!=self.window:
      context = b'\n' * self.window
    x = np.reshape([b for b in context], (1, self.window, 1)) / 255.0
    prediction = self.model.predict(x, verbose=0).flatten()
    frequencies = {i: prob+1e-8 for i, prob in enumerate(prediction)}
    if memoize: self.completions[context] = frequencies
    return frequencies

  def save(self, filename):
    # Save the model weights and configuration
    model_config = {
      'model_json': self.model.to_json(),
      'window': self.window
    }
    self.model.save_weights(f'{filename}.weights.h5')
    with open(filename, 'w') as f:
      json.dump(model_config, f)

  def load(self, filename):
    # Load model configuration and weights
    with open(filename, 'r') as f:
      model_config = json.load(f)
    self.window = model_config['window']
    model_json = model_config['model_json']
    self.model = tf.keras.models.model_from_json(model_json)
    self.model.load_weights(f'{filename}.weights.h5')
    return self


#############################################################


class Compressor:

  def __init__(self, predictor, Code):
    self.predictor = predictor
    self.Code = Code
    self.cached_codes = {}
  
  def contextual_code(self, context, memoize=True):
    if context in self.cached_codes:
      code = self.cached_codes[context]
    else:
      symbol_probabilities = self.predictor.frequencies_given_context(context)
      code = self.Code(symbol_probabilities)
      if memoize: self.cached_codes[context] = code
    return code

  def encode_symbol(self, context, symbol, memoize=True):
    code = self.contextual_code(context, memoize)
    return code.encode(symbol)

  def decode_symbol(self, context, bitarr, index, memoize=True):
    code = self.contextual_code(context, memoize)
    return code.decode(bitarr, index)
  
  def encode(self, text, context=None):
    out = bitarray()
    for index in range(len(text)):
      context = self.predictor.context(text, index, context)
      out.extend(self.encode_symbol(context, text[index]))
    return out.tobytes() + (len(out)%8).to_bytes()
    
  def decode(self, encoded_text, context=None):
    encoded_text_len_mod_8 = encoded_text[-1]
    encoded_bits = bitarray()
    encoded_bits.frombytes(encoded_text)
    encoded_bits = encoded_bits[:-8-(8-encoded_text_len_mod_8)%8]
    out = bytearray(context if context else b'')
    index = 0
    while index < len(encoded_bits):
      context = self.predictor.context(out, len(out))
      symbol, new_index = self.decode_symbol(context, encoded_bits, index)
      if symbol is None: break
      out.append(symbol)
      index = new_index
    return bytes(out)