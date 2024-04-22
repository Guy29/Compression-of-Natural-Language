import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
import json

class LSTMPredictor:
    def __init__(self, basis_text, window):
        self.window = window
        self.num_classes = 256
        self.model = self._build_model()
        if basis_text: self.train(basis_text)

    def _build_model(self):
        model = Sequential()
        model.add(LSTM(256, input_shape=(self.window, 1)))
        model.add(Dropout(0.2))
        model.add(Dense(self.num_classes, activation='softmax'))
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
        y = to_categorical(dataY, num_classes=self.num_classes)  # Ensure correct dimension

        self.model.fit(X, y, epochs=1, batch_size=128)

    def predict(self, input_bytes):
        last_window_bytes = input_bytes[-self.window:]
        x = np.reshape([b for b in last_window_bytes], (1, self.window, 1)) / 255.0
        prediction = self.model.predict(x, verbose=0).flatten()
        return {i: prob for i, prob in enumerate(prediction)}

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



training_books = {
    "pg1661.txt": "Sherlock Holmes",
    "pg1342.txt": "Pride and Prejudice",
    "pg1399.txt": "Anna Karenina",
    "pg1400.txt": "Great Expectations",
    "pg2554.txt": "Crime and Punishment"
    }


#predictor = LSTMPredictor(None, window=10)
#predictor.save('test-lstm-10')
#predictor.load('test-lstm-10')

while True:
  #break
  for fname, book_title in training_books.items():
    print(f'Training on: {book_title}')
  
    text   = open('../../../Data/books/' + fname,'rb').read()
    starts = list(range(0,len(text),100000))
    
    for start in starts:
      part = text[start:start+100000]
      predictor = LSTMPredictor(None, window=40)
      predictor.load('test-lstm-10')
      predictor.train(part)
      predictor.save('test-lstm-10')

# Predict using a sample byte sequence
sample_bytes = b"Sometimes I'll start a sentence, and I don't even know where it's"

for _ in range(50):
  prediction = predictor.predict(sample_bytes)
  _, most_likely = max((a,b) for (b,a) in prediction.items())
  sample_bytes += most_likely.to_bytes()

print(sample_bytes)
print(sample_bytes.decode('utf8'))