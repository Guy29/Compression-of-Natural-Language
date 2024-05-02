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

if __name__ == "__main__":

    # Loading a pre-trained Predictor and creating the corresponding Compressor

    rnn_predictor  = RNNPredictor(None, window=10)
    rnn_predictor.load('rnn-10')
    rnn_compressor = Compressor(predictor = rnn_predictor, Code = Arithmetic)


    # Encoding-decoding test

    inigo_text     = b'Hello. My name is Inigo Montoya. You killed my father. Prepare to die.'
    inigo_encoding = rnn_compressor.encode(inigo_text)
    inigo_decoding = rnn_compressor.decode(inigo_encoding)

    print(f'Original text: {inigo_text}')
    print(f'Encoded text : {inigo_encoding.hex()}')
    print(f'Decoded text : {inigo_decoding}')


    # Decoding noise to generate completions

    print('\nThe pre-trained RNN predictor generates the following example completion for the word "Elizabeth":')
    print(rnn_compressor.decode(randbytes(50)+b'\0', context=b'Elizabeth ').decode('utf8').__repr__())


    # Estimating compression ratio on unseen data
    
    rnn_huffman_compressor = Compressor(predictor = rnn_predictor, Code = Huffman)

    with open('../../Data/books/pg1661.txt','rb+') as f:
      test_text = f.read()[10000:11000]
      original_length = len(test_text)
      compressed_text = rnn_huffman_compressor.encode(test_text)
      compressed_length = len(compressed_text)
      print(f'\nEstimated compression ratio: {original_length/compressed_length}')