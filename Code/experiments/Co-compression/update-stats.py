# Running this script will update "stats.json" with new data
#   about the available books saved in "../../../Data/books", what the compressed
#   size of each is (using different compression algorithms) as well
#   as the sizes of the co-compressions of pairs of books.

import os, json, collections
from itertools import combinations_with_replacement
import zlib, lzma, gzip, bz2

books_location = '../../../Data/books/'

# NonCompressor class returns data without compression
class NonCompressor:
  def compress(self, b): return b


# Dictionary of different compression methods (including no compression)
libs_dict = {'zlib': zlib, 'lzma': lzma, 'gzip': gzip, 'bz2': bz2, 'no_compression': NonCompressor()}


class Stats:
  
  def __init__(self, filename):
    # Load known stats about books
    self.source_filename = filename
    try:
      with open(filename) as f:
        self.stats = json.load(f)
    except FileNotFoundError:
      def d(): return collections.defaultdict(d)
      self.stats = d()
  
  def update_book_filenames(self):
    # Load list of existing book files
    self.book_filenames = os.listdir(books_location)
  
  def update_book_titles(self):
    # Iterate over books in books_location and store book titles corresponding to file names
    for book_name in self.book_filenames:
      if book_name not in self.stats['book_titles']:
        with open(books_location + book_name,'rb') as bk:
          title = bk.read(200).split(b'\r')[0].split(b'eBook of ')[-1].decode()
        self.stats['book_titles'][book_name] = title

  def update_single_compression_sizes(self):
    # Iterate over books in books_location
    for book_name in self.book_filenames:

      # If you find a new book, add its compressed size to the stats ...
      if book_name not in self.stats['single_book_compression_sizes']:
        self.stats['single_book_compression_sizes'][book_name] = {}
      
      # ... for each compression algorithm you know
      for lib_name,compression_method in libs_dict.items():
        if lib_name not in self.stats['single_book_compression_sizes'][book_name]:
          with open(books_location + book_name,'rb+') as bk:
            self.stats['single_book_compression_sizes'][book_name][lib_name] = \
              len(compression_method.compress(bk.read()))

  def update_pair_compression_sizes(self):
    # Iterate over pairs of books (with replacement)
    for book_name1, book_name2 in combinations_with_replacement(self.book_filenames, 2):
      # Add the size of their co-compression to the stats
      for lib_name,compression_method in libs_dict.items():
        if lib_name not in self.stats['book_pair_compression_sizes'][book_name1][book_name2]:
          with open(books_location+book_name1,'rb+') as bk1, open(books_location+book_name2,'rb+') as bk2:
            self.stats['book_pair_compression_sizes'][book_name1][book_name2][lib_name] = \
              len(compression_method.compress(bk1.read()+bk2.read()))

  def save_data(self, filename):
    # Save the updated stats  
    with open(filename,'w+') as f:
      json.dump(self.stats, f, indent=2)
  
  def update_all_and_save(self):
    self.update_book_filenames()
    self.update_book_titles()
    self.update_single_compression_sizes()
    self.update_pair_compression_sizes()
    self.save_data(self.source_filename)


S = Stats('stats.json')
S.update_all_and_save()