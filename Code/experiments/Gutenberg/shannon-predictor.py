from heapq         import heappop, heappush, heapify
from collections   import Counter
from random        import random
from bitarray      import bitarray, decodetree
from bitarray.util import huffman_code
from time          import time


#############################################################

# Overwriting bitarray's huffman_code() function as this implementation runs faster

def huffman_code(probability_dict):
  """
  Takes a dictionary mapping symbols to their probabilities
    e.g. {'a': 0.25, 'b': 0.5, 'c': 0.25}
  Returns a dictionary that maps symbols to binary encodings as strings.
    e.g. {'c': '11', 'a': '10', 'b': '0'}
  """
  pairs = [(probability,token,token) for token,probability in probability_dict.most_common()]
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
    else: labels[token] = bitarray(label)
  return labels


#############################################################


class Predictor:
  
  def __init__(self, text, window=6):
    self.window = window
    self.cached_huffman_trees = {}
    self.train(text)
  
  def train(self, text):
    
    self.completions = {}
    
    for i in range(len(text)-self.window+1):
      stub = text[i:i+self.window-1]
      if stub in self.completions:
        self.completions[stub].update([text[i+self.window-1]])
      else: self.completions[stub] = Counter([text[i+self.window-1]])
    
    for stub in self.completions:
      for completion in self.completions[stub]:
        self.completions[stub][completion] *= 10000
      self.completions[stub].update(bytes(range(256)))
    
    self.byte_counts = Counter(text)
    self.byte_counts.update(bytes(range(256)))
    
    self.cached_huffman_trees[''] = huffman_code(self.byte_counts)
  
  def predict(self, text, count=1):
    stub = text[1-self.window:]
    assert len(stub) == self.window-1
    out = stub
    while len(out) < self.window - 1 + count:
      completions = self.completions.get(stub, self.byte_counts)
      index = random() * completions.total()
      for symbol,symbol_count in completions.most_common():
        if index >= symbol_count: index -= symbol_count
        else: out += bytes([symbol]); break
      stub = out[1-self.window:]
    return out[self.window-1:]
  
  def encode_byte(self, text, index):
    stub = text[index-self.window+1:index]
    if stub in self.cached_huffman_trees:
      tree = self.cached_huffman_trees[stub]
    elif stub in self.completions:
      tree = huffman_code(self.completions[stub])
      self.cached_huffman_trees[stub] = tree
    else:
      tree = self.cached_huffman_trees['']
    return tree[text[index]]
  
  def encode(self, text):
    out = bitarray()
    for i in range(len(text)):
      out.extend(self.encode_byte(text,i))
    return out.tobytes()


#############################################################


war_and_peace = open('books/pg2600.txt','rb+').read()

war_and_peace_predictor = Predictor(war_and_peace, window=5)

print('\nThe predictor trained on War and Peace generates the ' +\
      'following example completions for the word "Nicholas":\n')
      
for i in range(20):
  print(war_and_peace_predictor.predict(b'Nicholas', 30))


#############################################################

# Use the predictor trained on War and Peace to compress
#   The Count of Monte Cristo

monte_cristo = open('books/pg1184.txt','rb+').read()

t0 = time()
compressed_monte_cristo = war_and_peace_predictor.encode(monte_cristo)

print(f'\nText of The Count of Monte Cristo of length {len(monte_cristo)} bytes '+\
      f'compressed to {len(compressed_monte_cristo)} bytes in {time()-t0} seconds.')