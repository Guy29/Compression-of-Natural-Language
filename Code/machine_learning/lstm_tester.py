import sys
sys.path.insert(0, '../libraries')

import pandas      as     pd
from   random      import randbytes
from   codes       import Huffman, Arithmetic
from   predictors  import Predictor, Compressor

#############################################################

import json
import numpy      as np
import tensorflow as tf
from   random     import random
from   tensorflow.keras.models import Sequential
from   tensorflow.keras.layers import LSTM, Input, Dense, Dropout
from   tensorflow.keras.utils  import to_categorical


class LSTMPredictor(Predictor):
  
  def __init__(self, basis_text, window):
    self.window = window
    self.model = self._build_model()
    if basis_text: self.train(basis_text)
    self.completions = {}

  def _build_model(self):
    model = Sequential()
    model.add(Input(shape=(self.window,1)))
    model.add(LSTM(256))
    model.add(Dropout(0.2))
    model.add(Dense(256, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model
  
  def context(self, text, index, previous_context=None):
    return bytes(text[index-self.window:index]) if index-self.window>=0 else b'\n'*self.window

  def train(self, data):
    dataX, dataY = [], []
    for i in range(len(data) - self.window):
      seq_in = data[i:i + self.window]
      seq_out = data[i + self.window]
      dataX.append([byte for byte in seq_in])
      dataY.append(seq_out)

    X = np.reshape(dataX, (len(dataX), self.window, 1)) / 255.0
    y = to_categorical(dataY, num_classes=256)

    self.model.fit(X, y, epochs=1, batch_size=2048)
  
  def frequencies_given_context(self, context, memoize=0):
    if context in self.completions:
      return self.completions[context]
    x = np.reshape([b for b in context], (1, self.window, 1)) / 255.0
    prediction = self.model.predict(x, verbose=0).flatten()
    frequencies = {i: prob+1e-8 for i, prob in enumerate(prediction)}
    if random() < memoize: self.completions[context] = frequencies
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

if __name__ == "__main__":

    # Loading a pre-trained Predictor and creating the corresponding Compressor

    lstm_predictor  = LSTMPredictor(None, window=10)
    lstm_predictor.load('lstm-10')
    lstm_compressor = Compressor(predictor = lstm_predictor, Code = Arithmetic)


    # Encoding-decoding test

    inigo_text     = b'Hello. My name is Inigo Montoya. You killed my father. Prepare to die.'
    inigo_encoding = lstm_compressor.encode(inigo_text)
    inigo_decoding = lstm_compressor.decode(inigo_encoding)

    print(f'Original text: {inigo_text}')
    print(f'Encoded text : {inigo_encoding.hex()}')
    print(f'Decoded text : {inigo_decoding}')
    

    # Decoding noise to generate completions

    print('\nThe pre-trained LSTM predictor generates the following example completion for the word "Elizabeth":')
    print(lstm_compressor.decode(randbytes(50)+b'\0', context=b'Elizabeth ').decode('utf8').__repr__())
    

    # Estimating compression ratio on unseen data
    
    lstm_huffman_compressor = Compressor(predictor = lstm_predictor, Code = Huffman)

    with open('../../Data/books/pg1661.txt','rb+') as f:
      test_text = f.read()[10000:11000]
      original_length = len(test_text)
      compressed_text = lstm_huffman_compressor.encode(test_text)
      compressed_length = len(compressed_text)
      print(f'\nEstimated compression ratio: {original_length/compressed_length}')