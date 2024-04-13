from heapq         import heappop, heappush, heapify
from collections   import Counter
from random        import random, randbytes
from bitarray      import bitarray, decodetree
#from bitarray.util import huffman_code
from time          import time
from functools     import cache


#############################################################

# Writing my own class instead of using bitarray's huffman_code()
# function as this implementation runs faster

class HuffmanCode:
  
  def __init__(self, probability_dict):
    """
    Takes a dictionary mapping symbols to their probabilities
      e.g. {'a': 0.25, 'b': 0.5, 'c': 0.25}
    """
    pairs = [(probability,random(),symbol) for (symbol,probability) in probability_dict.items()]
    heapify(pairs)
    while len(pairs) > 1:
      probability1, _, symbol1 = heappop(pairs)
      probability2, _, symbol2 = heappop(pairs)
      new_pair = (probability1 + probability2, random(), {0:symbol1, 1:symbol2})
      heappush(pairs, new_pair)
    self.tree = pairs[0][2]
    self.symbol_encoding = HuffmanCode._reverse_lookup(self.tree)
   
  @staticmethod
  def _reverse_lookup(tree, prefix=None):
    if prefix is None: prefix = bitarray()
    reverse_lookup_table = {}
    for branch in [0,1]:
      if branch in tree:
        if type(tree[branch])==dict:
          reverse_lookup_table |= HuffmanCode._reverse_lookup(tree[branch],prefix+[branch])
        else:
          reverse_lookup_table |= {tree[branch]: prefix+[branch]}
    return reverse_lookup_table
  
  def encode(self, symbol):
    return self.symbol_encoding[symbol]
  
  def decode(self, bitarr, index):
    entry = self.tree
    while type(entry) == dict and index<len(bitarr):
      entry = entry[bitarr[index]]
      index += 1
    return (None if type(entry)==dict else entry), index


t = HuffmanCode({'a': 0.25, 'b': 0.5, 'c': 0.25})



#############################################################


class Predictor:
  
  def __init__(self, text, window=6):
    self.window = window
    self.cached_huffman_codes = {}
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
        self.completions[stub][completion] *= 1000000
      self.completions[stub].update(bytes(range(256)))
    
    self.byte_counts = Counter(text)
    self.byte_counts.update(bytes(range(256)))
    
    self.default_huffman_code = HuffmanCode(self.byte_counts)
  
  def huffman_for_stub(self, stub):
    if stub in self.cached_huffman_codes:
      huffman_code = self.cached_huffman_codes[stub]
    elif stub in self.completions:
      huffman_code = HuffmanCode(self.completions[stub])
      self.cached_huffman_codes[stub] = huffman_code
    else:
      huffman_code = self.default_huffman_code
    return huffman_code
  
  def encode(self, text):
    out = bitarray()
    for i in range(len(text)):
      stub = text[i-self.window+1:i]
      huffman_code = self.huffman_for_stub(stub)
      out.extend(huffman_code.encode(text[i]))
    return out.tobytes() + (len(out)%8).to_bytes()
    
  def decode(self, encoded_text, prefix=None):
    encoded_text_len_mod_8 = encoded_text[-1]
    encoded_bits = bitarray()
    encoded_bits.frombytes(encoded_text)
    encoded_bits = encoded_bits[:-8-(8-encoded_text_len_mod_8)%8]
    out = list(prefix) if prefix else []
    index = 0
    while index < len(encoded_bits):
      stub = bytes(out[len(out)-self.window+1:len(out)]) if len(out)>=self.window-1 else b''
      huffman_code = self.huffman_for_stub(stub)
      symbol, new_index = huffman_code.decode(encoded_bits, index)
      if symbol is None: break
      out.append(symbol)
      index = new_index
    return bytes(out)


#############################################################


war_and_peace = open('../../../Data/books/pg2600.txt','rb+').read()

war_and_peace_predictor = Predictor(war_and_peace, window=6)

inigo_encoding = war_and_peace_predictor.encode(b'My name is Inigo Montoya')
inigo_decoding = war_and_peace_predictor.decode(inigo_encoding)

print(inigo_encoding)
print(inigo_decoding)


print('\nThe predictor trained on War and Peace generates the ' +\
      'following example completions for the word "Nicholas":\n')
      
for i in range(20):
  print(war_and_peace_predictor.decode(randbytes(50)+b'\0', prefix=b'Nicholas'))


#############################################################

# Use the predictor trained on War and Peace to compress
#   The Count of Monte Cristo

monte_cristo = open('../../../Data/books/pg1184.txt','rb+').read()

t0 = time()
compressed_monte_cristo = war_and_peace_predictor.encode(monte_cristo)

print(f'\nText of The Count of Monte Cristo of length {len(monte_cristo)} bytes '+\
      f'compressed to {len(compressed_monte_cristo)} bytes in {time()-t0} seconds.')

# Text of The Count of Monte Cristo of length 2787236 bytes compressed to 962945 bytes in 80.86559343338013 seconds.


#############################################################

# And use it again, this time on the text of War and Peace itself

t0 = time()
compressed_war_peace = war_and_peace_predictor.encode(war_and_peace)

print(f'\nText of War and Peace of length {len(war_and_peace)} bytes '+\
      f'compressed to {len(compressed_war_peace)} bytes in {time()-t0} seconds.')

# Text of The Count of Monte Cristo of length 3359632 bytes compressed to 788962 bytes in 139.9738645553589 seconds.