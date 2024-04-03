# Running this script will update "stats.json" with new data
#   about the available books saved in "../../../Data/books", what the compressed
#   size of each is (using different compression algorithms) as well
#   as the sizes of the co-compressions of pairs of books.

import os, json
from itertools import combinations_with_replacement
import zlib, lzma, gzip, bz2

books_location = '../../../Data/books/'


# NonCompressor class returns data without compression
class NonCompressor:
  def compress(self, b): return b


# Dictionary of different compression methods (including no compression)
libs_dict = {'zlib': zlib, 'lzma': lzma, 'gzip': gzip, 'bz2': bz2, 
             'no_compression': NonCompressor()}


# Load known stats about books
with open('stats.json') as f:
  stats = json.load(f)


# Load list of existing book files
book_names = os.listdir(books_location)


# Iterate over books in books_location and store book titles corresponding to file names
for book_name in book_names:
  if book_name not in stats['book_titles']:
    with open(books_location + book_name,'rb') as bk:
      title = bk.read(200).split(b'\r')[0].split(b'eBook of ')[-1].decode()
    stats['book_titles'][book_name] = title


# Iterate over books in books_location
for book_name in book_names:

  # If you find a new book, add its compressed size to the stats ...
  if book_name not in stats['single_book_compression_sizes']:
    stats['single_book_compression_sizes'][book_name] = {}
  
  # ... for each compression algorithm you know
  for lib_name,compression_method in libs_dict.items():
    if lib_name not in stats['single_book_compression_sizes'][book_name]:
      with open(books_location + book_name,'rb+') as bk:
        stats['single_book_compression_sizes'][book_name][lib_name] = \
          len(compression_method.compress(bk.read()))


# Iterate over pairs of books (with replacement)
for book_name1, book_name2 in combinations_with_replacement(book_names, 2):
  
  # If you find a new book ...
  if book_name1 not in stats['book_pair_compression_sizes']:
    stats['book_pair_compression_sizes'][book_name1] = {}
  
  # ... or a new pairing of two books ...
  if book_name2 not in stats['book_pair_compression_sizes'][book_name1]:
    stats['book_pair_compression_sizes'][book_name1][book_name2] = {}
  
  # ... add the size of their co-compression to the stats
  for lib_name,compression_method in libs_dict.items():
    if lib_name not in stats['book_pair_compression_sizes'][book_name1][book_name2]:
      with open(books_location+book_name1,'rb+') as bk1, open(books_location+book_name2,'rb+') as bk2:
        stats['book_pair_compression_sizes'][book_name1][book_name2][lib_name] = \
          len(compression_method.compress(bk1.read()+bk2.read()))


# Save the updated stats  
with open('stats.json','w+') as f:
  json.dump(stats, f, indent=2)