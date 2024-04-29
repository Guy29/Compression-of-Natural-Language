import os
from rnn_tester import RNNPredictor

rnn_predictor  = RNNPredictor(None, window=10)
rnn_predictor.load('rnn-10')

book_fnames = os.listdir('../../Data/books')
book_fnames = ['44010.txt']

while True:
    for fname in book_fnames:
      print(f'Training on {fname}')
      text = open('../../Data/books/'+fname,'rb+').read()
      rnn_predictor.train(text)
      print('Saving')
      rnn_predictor.save('rnn-10')