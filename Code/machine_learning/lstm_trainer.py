import os, numpy
from nn_predictors import LSTMPredictor

lstm_predictor  = LSTMPredictor(None, window=10)
lstm_predictor.load('lstm-10')

book_fnames = os.listdir('../../Data/books')

while True:
    for fname in book_fnames:
      text = open('../../Data/books/'+fname,'rb+').read()
      if not b'Language: English' in text:
        print(f'Skipping {fname}')
        continue
      try:
        print(f'Training on {fname}')
        lstm_predictor.train(text)
        print('Saving')
        lstm_predictor.save('lstm-10')
      except numpy.core._exceptions._ArrayMemoryError:
        print(f'Skipping {fname}')
        continue