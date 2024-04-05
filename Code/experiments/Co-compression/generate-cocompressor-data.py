from co_compressor import *

stats = json.load(open('stats.json'))

outfile = open('practical-out.txt','w+')

count = 0
t0 = time.time()
# Iterate over books
for fname1 in stats['book_titles']:
  # Train a compressor on the current book
  Tcompressor = CoCompressor([f"{stats['books_location']}{fname1}"], compressor = lzma)

  # Iterate over books
  for fname2 in stats['book_titles']:
    with open(f"{stats['books_location']}{fname2}",'rb') as f:
      text = f.read()
    i,c = Tcompressor.compress(text)
    compressed_size = len(c)
    independently_compressed_size = len(lzma.compress(text))
    data = [fname1, fname2, stats['abbreviated_book_titles'][fname1], stats['abbreviated_book_titles'][fname2], i, compressed_size, independently_compressed_size, independently_compressed_size/compressed_size]
    count += 1
    print(*data[2:],count,time.time()-t0)
    outfile.write(','.join(map(str,data))+'\n')