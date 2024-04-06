import json, time
import zlib, lzma, gzip, bz2

class CoCompressor:
  
  def __init__(self, basis, compressor = lzma):
    self.uncompressed_prefix  = basis
    self.compressor = compressor
    self.train()
  
  def train(self):
    self.compressed_prefix = self.compressor.compress(self.uncompressed_prefix)
    
  def compress(self, byte_data):
    # Compress both the uncompressed prefix of this CoCompressor together with the byte data
    compressed_total = self.compressor.compress(self.uncompressed_prefix + byte_data)
    
    # Find the overlap with compressed_prefix
    for i in range(len(compressed_total)):
      if compressed_total[i] != self.compressed_prefix[i]: break
    return i.to_bytes(4) + compressed_total[i:]
  
  def decompress(self, compressed_byte_data):
    i = int.from_bytes(compressed_byte_data[:4])
    c = compressed_byte_data[4:]
    compressed_total = self.compressed_prefix[:i] + c
    total = self.compressor.decompress(compressed_total)
    byte_data = total[len(self.uncompressed_prefix):]
    return byte_data