import os, numpy
from nn_predictors import RNNPredictor

rnn_predictor  = RNNPredictor(None, window=10)
rnn_predictor.load('rnn-10')

book_fnames = os.listdir('../../Data/books')

while True:
    for fname in book_fnames:
      text = open('../../Data/books/'+fname,'rb+').read()
      if not b'Language: English' in text:
        print(f'Skipping {fname}')
        continue
      try:
        print(f'Training on {fname}')
        rnn_predictor.train(text)
        print('Saving')
        rnn_predictor.save('rnn-10')
      except numpy.core._exceptions._ArrayMemoryError:
        print(f'Skipping {fname}')
        continue