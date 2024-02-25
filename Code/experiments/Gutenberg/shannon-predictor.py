from heapq       import heappop, heappush, heapify
from collections import Counter
from random      import random


#############################################################


def huffman(pairs):
  """
  Takes a list of pairs of tokens and their probabilities
    e.g. [('a',0.25), ('b',0.5), ('c',0.25)]
  Returns a dictionary that maps tokens to binary encodings as strings.
    e.g. {'c': '11', 'a': '10', 'b': '0'}
  """
  pairs = [(probability,token,token) for token,probability in pairs]
  heapify(pairs)
  while len(pairs) > 1:
    leaf1 = probability1, _, __ = heappop(pairs)
    leaf2 = probability2, _, __ = heappop(pairs)
    new_pair = (probability1 + probability2, _, (leaf1,leaf2))
    heappush(pairs, new_pair)
  pairs = [('',pairs[0])]
  labels = {}
  while pairs:
    label, (_, _, token) = pairs.pop()
    if isinstance(token, tuple):
      pairs.append((label+'0', token[0]))
      pairs.append((label+'1', token[1]))
    else: labels[token] = label
  return labels


#############################################################


class Predictor:
  
  def __init__(self, text, window=6):
    self.window = window
    self.cached_encodings = {}
    self.train(text)
  
  def train(self, text):
    
    self.possibilities = {}
    
    for i in range(len(text)-self.window+1):
      stub = text[i:i+self.window-1]
      if stub in self.possibilities:
        self.possibilities[stub].update([text[i+self.window-1]])
      else: self.possibilities[stub] = Counter([text[i+self.window-1]])
    
    for stub in self.possibilities:
      for completion in self.possibilities[stub]:
        self.possibilities[stub][completion] *= 10000
      self.possibilities[stub].update(bytes(range(256)))
      total_count = self.possibilities[stub].total()
      self.possibilities[stub] = [(completion,count/total_count) for completion, count in self.possibilities[stub].most_common()]
    
    byte_counts = Counter(text)
    byte_counts.update(bytes(range(256)))
    total_byte_count = byte_counts.total()
    self.byte_frequencies = [(b,count/total_byte_count) for b,count in byte_counts.most_common()]
    self.cached_encodings[''] = huffman(self.byte_frequencies)
  
  def predict(self, text, count=1):
    stub = text[1-self.window:]
    assert len(stub) == self.window-1
    out = stub
    while len(out) < self.window - 1 + count:
      possibilities = self.possibilities.get(stub, self.byte_frequencies)
      probability = random()
      for completion,frequency in possibilities:
        if probability >= frequency: probability -= frequency
        else: out += bytes([completion]); break
      stub = out[1-self.window:]
    return out[self.window-1:]
  
  def encode_byte(self, text, index):
    stub = text[index-self.window+1:index]
    if stub in self.cached_encodings:
      encodings = self.cached_encodings[stub]
    elif stub in self.possibilities:
      encodings = huffman(self.possibilities[stub])
      self.cached_encodings[stub] = encodings
    else:
      encodings = self.cached_encodings['']
    return encodings[text[index]]
  
  def encode(self, text):
    return ''.join(self.encode_byte(text,i) for i in range(len(text)))


#############################################################


war_and_peace = open('books/pg2600.txt','rb+').read()
monte_cristo  = open('books/pg1184.txt','rb+').read()


war_and_peace_predictor = Predictor(war_and_peace)

for i in range(20):
  print(war_and_peace_predictor.predict(b'Nicholas', 30))
  

print(len(monte_cristo))
print(len(war_and_peace_predictor.encode(monte_cristo[:20000])))