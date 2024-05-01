import os, numpy
from lstm_tester import LSTMPredictor

lstm_predictor  = LSTMPredictor(None, window=10)
lstm_predictor.load('lstm-10')

book_fnames = os.listdir('../../Data/books')
#book_fnames = ['pg1342.txt']

while True:
    for fname in book_fnames[41:]:
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
        continue