import os, json, collections
import zlib, lzma, gzip, bz2
import pandas            as pd
import seaborn           as sns
import matplotlib.pyplot as plt
from collections   import defaultdict
from itertools     import combinations_with_replacement, product
from math          import log
from statistics    import median, variance
from co_compressor import CoCompressor



# NonCompressor class returns data without compression
class NonCompressor:
  def compress(self, b): return b


# Dictionary of different compression methods (including no compression)
libs_dict = {'zlib': zlib, 'lzma': lzma, 'gzip': gzip, 'bz2': bz2, 'no_compression': NonCompressor()}


# Function to return the size of a file given its name
def file_size(filename):
  with open(filename,'rb+') as f:
    return f.seek(0,2)


# Function that returns an empty recursive defaultdict
def rdd(): return defaultdict(rdd)


# Function that converts and existing dict to a recursive defaultdict
def to_rdd(d):
  return defaultdict(rdd,{k:(to_rdd(v) if isinstance(v,dict) else v) for k,v in d.items()})



class Stats:
  
  def __init__(self, filename):
    # Load known stats about books
    self.source_filename = filename
    try:
      with open(filename) as f:
        self.stats = json.load(f)
    except FileNotFoundError:
      self.stats = {}
    self.stats = to_rdd(self.stats)
  
  def update_book_filenames(self):
    # Load list of existing book files
    self.book_filenames = os.listdir(self.stats['books_location'])
  
  def update_book_titles(self):
    # Iterate over books in books_location and store book titles corresponding to file names
    for book_name in self.book_filenames:
      if book_name not in self.stats['book_titles']:
        with open(self.stats['books_location'] + book_name,'rb') as bk:
          title = bk.read(200).split(b'\r')[0].split(b'eBook of ')[-1].split(b'EBook of ')[-1].decode()
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
          with open(self.stats['books_location'] + book_name,'rb+') as bk:
            self.stats['single_book_compression_sizes'][book_name][lib_name] = \
              len(compression_method.compress(bk.read()))

  def update_pair_compression_sizes(self):
    # Iterate over pairs of books (with replacement)
    for book_name1, book_name2 in combinations_with_replacement(self.book_filenames, 2):
      # Add the size of their co-compression to the stats
      for lib_name,compression_method in libs_dict.items():
        if lib_name not in self.stats['book_pair_compression_sizes'][book_name1][book_name2]:
          with open(self.stats['books_location']+book_name1,'rb+') as bk1, open(self.stats['books_location']+book_name2,'rb+') as bk2:
            self.stats['book_pair_compression_sizes'][book_name1][book_name2][lib_name] = \
              len(compression_method.compress(bk1.read()+bk2.read()))
  
  def update_cocompressor_performance(self):
    # Iterate over books
    for fname1 in self.book_filenames:
      # Placeholder for a compressor trained on the current book
      compressor = None

      # Iterate over books
      for fname2 in self.book_filenames:
        
        if self.stats['cocompressor_performance'][fname1][fname2]: continue
        
        if not compressor:
          with open(f"{self.stats['books_location']}{fname1}",'rb+') as f:
            compressor_basis = f.read()
          compressor = CoCompressor(compressor_basis, compressor = lzma)
        
        with open(f"{self.stats['books_location']}{fname2}",'rb') as f:
          text = f.read()
        compressed_size = len(compressor.compress(text))
        independently_compressed_size = self.stats['single_book_compression_sizes'][fname2]['lzma']
        self.stats['cocompressor_performance'][fname1][fname2] = {'compressed_size': compressed_size, 'ratio': independently_compressed_size/compressed_size}

  def save_data(self, filename):
    # Save the updated stats  
    with open(filename,'w+') as f:
      json.dump(self.stats, f, indent=2, ensure_ascii=False)
  
  def update_all_and_save(self):
    self.update_book_filenames()
    self.update_book_titles()
    self.update_single_compression_sizes()
    self.update_pair_compression_sizes()
    self.update_cocompressor_performance()
    self.save_data(self.source_filename)
    
  def compute_similarity_matrix(self):
    # This method will read stats and create a similarity
    #   matrix for pairs of books.

    matrix = pd.DataFrame(columns = self.book_filenames, index = self.book_filenames)

    # Iterate over pairs of books, filling out the matrix
    for book1_fname, book2_fname in product(self.book_filenames, repeat=2):

      book1_compressed_size = self.stats['single_book_compression_sizes'][book1_fname]['lzma']
      book2_compressed_size = self.stats['single_book_compression_sizes'][book2_fname]['lzma']
      
      pair_sizes = self.stats['book_pair_compression_sizes']
      
      b1,b2 = book1_fname, book2_fname
      pair_compression_size = (pair_sizes[b1][b2] if (b2 in pair_sizes[b1]) else pair_sizes[b2][b1])['lzma']
    
      additional_information = (pair_compression_size - book1_compressed_size) / book2_compressed_size
      similarity             = 1 - additional_information
    
      matrix.at[book1_fname, book2_fname] = similarity
      
    matrix = matrix.infer_objects(copy=False)
    self.similarity_matrix = matrix
  
  def compute_cocomp_matrix(self):
    matrix = pd.DataFrame(columns = self.book_filenames, index = self.book_filenames)
    for fname1,fname2 in product(self.book_filenames, repeat=2):
      matrix.at[fname1, fname2] = log(self.stats['cocompressor_performance'][fname1][fname2]['ratio'])
    matrix = matrix.infer_objects(copy=False)
    self.cocomp_matrix = matrix
    
  def draw_heatmap(self, matrix, title, sort_by, filename):
    
    # Sort rows and columns of the matrix
    if   sort_by == 'file size':
      sorted_book_filenames = sorted(self.book_filenames, key = lambda fname: file_size(self.stats['books_location'] + fname))
      matrix = matrix.loc[sorted_book_filenames[::-1], sorted_book_filenames]
    elif sort_by == 'median':
      matrix = matrix[matrix.median(axis=0).sort_values().index].loc[matrix.median(axis=1).sort_values().index]
      matrix = matrix.iloc[::-1,::-1]

    # Rename the columns in rows in the matrix from book filenames to the corresponding abbreviated book titles
    matrix = matrix.rename(
                      columns = self.stats['abbreviated_book_titles'],
                      index   = self.stats['abbreviated_book_titles'])

    # Creating the heatmap
    plt.figure(figsize=(20, 15))
    heatmap = sns.heatmap(matrix, cmap='viridis')
    plt.title(title, fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.savefig(filename, dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    
  def draw_similarity_heatmap(self, sort_by, filename):
    self.draw_heatmap(self.similarity_matrix, 'Book similarity', sort_by, filename)
    
  def draw_cocomp_heatmap(self, sort_by, filename):
    self.draw_heatmap(self.cocomp_matrix, 'CoCompressor similarity', sort_by, filename)
  
  def print_most_least_similar(self):
    # Get a dict copy of the data
    similarity_dict = self.similarity_matrix.to_dict()
      
    all_scores = [(value, bk1, bk2) for (bk1,bk2), value in self.similarity_matrix.stack().items() if bk1!=bk2]
    all_scores.sort()

    # Function to print human-friendly book names instead of Gutenberg filenames
    def title(book_filename):
      return f"{self.stats['book_titles'][book_filename]} ({book_filename})"

    # Get the top and bottom pairs of books and replace book file names with book titles
    top    = [(score,title(bk1),title(bk2)) for (score,bk1,bk2) in all_scores[:10]]
    bottom = [(score,title(bk1),title(bk2)) for (score,bk1,bk2) in all_scores[-10:]]


    # Display them
    df = pd.DataFrame(top + [('...',)*3] + bottom, columns=['Score', 'Book 1', 'Book 2'])
    print(df.to_string(index=False))
  
  def draw_cocomp_performance(self, filename, text_selection=None, ylim=(0.7,1.3)):
    
    if text_selection is None:
      text_selection = self.book_filenames
    
    performances = {}
    for fname in text_selection:
      ratios = [stats['ratio'] for text,stats in self.stats['cocompressor_performance'][fname].items()]
      performances[self.stats['abbreviated_book_titles'][fname]] = sorted(ratios, reverse=True)
    
    median_performance = sorted(performances, key=lambda title: median(performances[title]), reverse=True)
    extreme_median_performances = median_performance[:3]+median_performance[-3:]
    
    all_titles = set(performances)

    plt.figure(figsize=(10, 6))
    
    for title in all_titles - set(extreme_median_performances):
      plt.plot(performances[title], color='#aaa', linestyle='dotted')
    for title in extreme_median_performances:
      plt.plot(performances[title], label=title)
    
    plt.xticks([])
    plt.grid(axis='y', linestyle='--')

    plt.xlim(2, 96)
    plt.ylim(*ylim)

    plt.legend()
    plt.xlabel('Texts sorted by ease of compression')
    plt.ylabel('Co-compressor performance compared to LZMA')
    plt.title('Co-compressor performances')

    #plt.show()
    plt.savefig(filename, dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()



if __name__ == "__main__":
    S = Stats('stats.json')
    S.update_all_and_save()
    #S.compute_similarity_matrix()
    #S.draw_similarity_heatmap(sort_by='file size', filename='fig_co-compression_file_size.png')
    #S.draw_similarity_heatmap(sort_by='median', filename='fig_co-compression_median.png')
    #S.compute_cocomp_matrix()
    #S.draw_cocomp_heatmap(sort_by='file size', filename='fig_cocomp_file_size.png')
    #S.draw_cocomp_heatmap(sort_by='median', filename='fig_cocomp_median.png')
    #S.print_most_least_similar()
    S.draw_cocomp_performance(filename = 'fig_cocomp_performance.png',
                              text_selection = [fname for fname in S.book_filenames if    (fname.startswith('pg'))])
    S.draw_cocomp_performance(filename = 'fig_cocomp_performance_best.png',
                              text_selection = [fname for fname in S.book_filenames if not(fname.startswith('pg')) or fname=='pg145.txt'],
                              ylim = (1,1.3))