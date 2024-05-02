import sys
sys.path.insert(0, '../libraries')

import pandas      as     pd
from   random      import randbytes
from   codes       import Huffman, Arithmetic
from   predictors  import NNPredictor, Compressor

from   tensorflow.keras.models import Sequential
from   tensorflow.keras.layers import LSTM, SimpleRNN, Input, Dense, Dropout

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