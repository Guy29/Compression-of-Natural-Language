import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.utils import to_categorical
import pickle

class LSTMPredictor:
    def __init__(self, basis_text, window):
        self.window = window
        self.num_classes = 256  # Full byte range
        self.model = self._build_model()
        self.train(basis_text)

    def _build_model(self):
        model = Sequential()
        model.add(LSTM(256, input_shape=(self.window, 1)))
        model.add(Dropout(0.2))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam')
        return model

    def train(self, data):
        # Ensuring all byte values are represented
        unique_bytes = set(data)
        if len(unique_bytes) < self.num_classes:
            print(f"Warning: Only {len(unique_bytes)} unique bytes found. Model expects {self.num_classes}.")

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

# Usage remains the same


# Example basis text and usage
basis_text = open('../../../Data/books/pg10.txt','rb').read()[:2000]
predictor = LSTMPredictor(basis_text, window=5)

# Predict using a sample byte sequence
sample_bytes = b"Hello world! This is an example of text to byte prediction."

for _ in range(50):
  prediction = predictor.predict(sample_bytes)
  _, most_likely = max((a,b) for (b,a) in prediction.items())
  sample_bytes += most_likely.to_bytes()

print(sample_bytes)
print(sample_bytes.decode('utf8'))