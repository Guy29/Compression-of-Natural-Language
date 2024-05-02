import sys
sys.path.insert(0, '../libraries')

import pandas      as     pd
from   random      import randbytes
from   codes       import Huffman, Arithmetic
from   predictors  import NNPredictor, Compressor

from   tensorflow.keras.models import Sequential
from   tensorflow.keras.layers import LSTM, SimpleRNN, Input, Dense, Dropout

#############################################################


class RNNPredictor(NNPredictor):

  def _build_model(self):
    model = Sequential()
    model.add(Input(shape=(self.window,1)))
    model.add(SimpleRNN(256))
    model.add(Dropout(0.2))
    model.add(Dense(256, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

#############################################################


class LSTMPredictor(NNPredictor):

  def _build_model(self):
    model = Sequential()
    model.add(Input(shape=(self.window,1)))
    model.add(LSTM(256))
    model.add(Dropout(0.2))
    model.add(Dense(256, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model


#############################################################

if __name__ == "__main__":

    # Loading a pre-trained Predictors

    rnn_predictor  = RNNPredictor(None, window=10)
    rnn_predictor.load('rnn-10')

    lstm_predictor  = LSTMPredictor(None, window=10)
    lstm_predictor.load('lstm-10')
    
    for predictor in [rnn_predictor, lstm_predictor]:
    
      print('\n\n----',type(predictor).__name__,'----')
    
      arithmetic_compressor = Compressor(predictor = predictor, Code = Arithmetic)
      huffman_compressor    = Compressor(predictor = predictor, Code = Huffman)

      # Encoding-decoding test

      inigo_text     = b'Hello. My name is Inigo Montoya. You killed my father. Prepare to die.'
      inigo_encoding = huffman_compressor.encode(inigo_text)
      inigo_decoding = huffman_compressor.decode(inigo_encoding)

      print(f'Original text: {inigo_text}')
      print(f'Encoded text : {inigo_encoding.hex()}')
      print(f'Decoded text : {inigo_decoding}')


      # Decoding noise to generate completions

      prefix = "Elizabeth"
      print(f'\nExample completions for "{prefix}":')
      print(arithmetic_compressor.decode(randbytes(50)+b'\0', context=bytes(prefix,'utf8')).decode('utf8').__repr__())


      # Estimating compression ratio on unseen data

      with open('../../Data/books/pg1661.txt','rb+') as f:
        test_text = f.read()[10000:11000]
        original_length = len(test_text)
        compressed_text = huffman_compressor.encode(test_text)
        compressed_length = len(compressed_text)
        print(f'\nEstimated compression ratio: {original_length/compressed_length}')