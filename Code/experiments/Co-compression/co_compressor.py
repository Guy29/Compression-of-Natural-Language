import json, time
import zlib, lzma, gzip, bz2

class CoCompressor:
  
  def __init__(self, filenames, compressor = lzma):
    self.filenames  = filenames
    self.compressor = compressor
    self.train()
  
  def train(self):
    # Concatenate the contents of the input texts
    self.uncompressed_prefix = []
    for fname in self.filenames:
      with open(fname, 'rb') as f:
        self.uncompressed_prefix.append(f.read())
    self.uncompressed_prefix = b''.join(self.uncompressed_prefix)
    
    # Compress them
    self.compressed_prefix = self.compressor.compress(self.uncompressed_prefix)
    
  def compress(self, byte_data):
    # Compress both the uncompressed prefix of this CoCompressor together with the byte data
    compressed_total = self.compressor.compress(self.uncompressed_prefix + byte_data)
    
    # Find the overlap with compressed_prefix
    for i in range(len(compressed_total)):
      if compressed_total[i] != self.compressed_prefix[i]: break
    return (i,compressed_total[i:])