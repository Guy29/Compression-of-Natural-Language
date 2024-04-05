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


books_location = '../../../Data/books/'

stats = json.load(open('stats.json'))

best_compressor_estimates = ['pg2600.txt', 'pg1184.txt', 'pg996.txt', 'pg145.txt', 'pg28054.txt', 'pg1399.txt', 'pg2701.txt', 'pg4300.txt', 'pg5197.txt', 'pg1260.txt', 'pg1259.txt', 'pg730.txt', 'pg1400.txt', 'pg2554.txt', 'pg514.txt', 'pg37106.txt', 'pg98.txt', 'pg6593.txt', 'pg768.txt', 'pg100.txt', 'pg345.txt', 'pg4085.txt', 'pg205.txt', 'pg158.txt', 'pg2160.txt', 'pg36034.txt', 'pg6761.txt', 'pg72969.txt', 'pg1661.txt', 'pg1497.txt', 'pg30254.txt', 'pg1342.txt', 'pg161.txt', 'pg25344.txt', 'pg1727.txt', 'pg42324.txt', 'pg41445.txt', 'pg1998.txt', 'pg84.txt', 'pg45.txt', 'pg72972.txt', 'pg408.txt', 'pg174.txt', 'pg8492.txt', 'pg24869.txt', 'pg394.txt', 'pg15399.txt', 'pg10.txt', 'pg2641.txt', 'pg16389.txt', 'pg74.txt', 'pg67979.txt', 'pg6130.txt', 'pg2814.txt', 'pg3296.txt', 'pg2591.txt', 'pg36.txt', 'pg244.txt', 'pg600.txt', 'pg2852.txt', 'pg120.txt', 'pg4363.txt', 'pg219.txt', 'pg23.txt', 'pg64317.txt', 'pg8800.txt', 'pg3207.txt', 'pg1232.txt', 'pg72971.txt', 'pg43.txt', 'pg10007.txt', 'pg76.txt', 'pg16.txt', 'pg35.txt', 'pg2680.txt', 'pg72967.txt', 'pg46.txt', 'pg27827.txt', 'pg72970.txt', 'pg55.txt', 'pg7370.txt', 'pg2542.txt', 'pg5200.txt', 'pg844.txt', 'pg5827.txt', 'pg11.txt', 'pg16328.txt', 'pg72968.txt', 'pg1513.txt', 'pg67098.txt', 'pg16119.txt', 'pg72966.txt', 'pg58585.txt', 'pg1952.txt', 'pg1080.txt', 'pg72950.txt', 'pg2000.txt']

outfile = open('practical-out.txt','w+')

count = 0
t0 = time.time()
# Iterate over books
for fname1 in best_compressor_estimates:
  # Train a compressor on the current book
  Tcompressor = CoCompressor([f'{books_location}{fname1}'], compressor = lzma)

  # Iterate over books
  for fname2 in stats['book_titles']:
    with open(f'{books_location}{fname2}','rb') as f:
      text = f.read()
    i,c = Tcompressor.compress(text)
    compressed_size = len(c)
    independently_compressed_size = len(lzma.compress(text))
    data = [fname1, fname2, stats['abbreviated_book_titles'][fname1], stats['abbreviated_book_titles'][fname2], i, compressed_size, independently_compressed_size, independently_compressed_size/compressed_size]
    count += 1
    print(*data[2:],count,time.time()-t0)
    outfile.write(','.join(map(str,data))+'\n')