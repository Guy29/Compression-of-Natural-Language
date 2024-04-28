from heapq     import heappop, heappush, heapify
from random    import random
from bitarray  import bitarray
from math      import log, floor, ceil
from bisect    import bisect_left, bisect_right
from abc       import ABC, abstractmethod




#############################################################

class Code(ABC):
  @abstractmethod
  def __init__(self, probability_dict):
    """
    Takes a dictionary mapping symbols to their probabilities
      e.g. {'a': 0.25, 'b': 0.5, 'c': 0.25}
    """
    pass
  
  @abstractmethod
  def encode(self, symbol): pass
  
  @abstractmethod
  def decode(self, bitarr, index): pass




#############################################################

# Writing my own class instead of using bitarray's code()
# function as this implementation runs faster

class Huffman(Code):

  name = 'Huffman'
  
  def __init__(self, probability_dict):
    self.probability_dict = probability_dict
    self.tree             = None
    self.symbol_encoding  = None
  
  def build_tree(self):
    salt = 0
    pairs = [(probability,(salt:=salt+1),symbol) for (symbol,probability) in self.probability_dict.items()]
    heapify(pairs)
    while len(pairs) > 1:
      probability1, _, symbol1 = heappop(pairs)
      probability2, _, symbol2 = heappop(pairs)
      new_pair = (probability1 + probability2, (salt:=salt+1), {0:symbol1, 1:symbol2})
      heappush(pairs, new_pair)
    self.tree = pairs[0][2]
  
  def build_symbol_encoding(self):
    tree_exists = self.tree
    if not tree_exists: self.build_tree()
    self.symbol_encoding = Huffman._reverse_lookup(self.tree)
    if not tree_exists: self.tree = None
   
  @staticmethod
  def _reverse_lookup(tree, prefix=None):
    if prefix is None: prefix = bitarray()
    reverse_lookup_table = {}
    for branch in [0,1]:
      if branch in tree:
        if type(tree[branch])==dict:
          reverse_lookup_table |= Huffman._reverse_lookup(tree[branch],prefix+[branch])
        else:
          reverse_lookup_table |= {tree[branch]: prefix+[branch]}
    return reverse_lookup_table
  
  def encode(self, symbol):
    if not self.symbol_encoding: self.build_symbol_encoding()
    return self.symbol_encoding[symbol]
  
  def decode(self, bitarr, index):
    if not self.tree: self.build_tree()
    entry = self.tree
    while type(entry) == dict and index<len(bitarr):
      entry = entry[bitarr[index]]
      index += 1
    return (None if type(entry)==dict else entry), index




#############################################################

class Arithmetic(Code):
  
  name = 'Arithmetic'
  
  def __init__(self, probability_dict):
    total = sum(probability_dict.values())
    intervals = [(frequency/total,symbol) for (symbol,frequency) in probability_dict.items()]
    intervals.sort(reverse=True)
    steps = [(0., 256)]
    for probability, symbol in intervals:
      prev_probability, prev_symbol = steps[-1]
      steps.append((prev_probability + probability, symbol))
    self.steps = steps
    self.intervals = {steps[i][1]: (steps[i-1][0],steps[i][0]) for i in range(1,len(steps))}
    
  def encode(self, symbol):
    interval_start, interval_end = self.intervals[symbol]
    interval_size = interval_end - interval_start
    scale = 2**floor(-log(interval_size, 2))
    while ceil(interval_end*scale) - ceil(interval_start*scale) < 2:
      scale *= 2
    return bitarray(bin(ceil(interval_start*scale + scale))[3:])
    
  def decode(self, bitarr, index):
    integer_representation = 0
    scale = 1
    start_index, end_index = 0, 1
    while start_index != end_index and index < len(bitarr):
      integer_representation *= 2
      integer_representation += bitarr[index]
      index += 1
      scale *= 2
      interval_start = (integer_representation / scale, 1e400)
      interval_end   = ((integer_representation + 1) / scale, -1e400)
      start_index = bisect_right(self.steps, interval_start)
      end_index   = bisect_left (self.steps, interval_end)
    if start_index != end_index: return (None, index)
    return (self.steps[end_index][1], index)


#############################################################