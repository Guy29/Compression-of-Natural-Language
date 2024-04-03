# This script will read stats from "stats.json" and
#   create a CSV file that contains a similarity
#   matrix for pairs of books.

import json

# Load book compression stats
with open('stats.json','r') as f:
  stats = json.load(f)

# Function to return the size of a file given its name
def file_size(filename):
  with open(filename,'rb+') as f:
    return f.seek(0,2)

# Load the book file names and sort them by size of file
book_names = list(stats['single_book_compression_sizes'].keys())
book_names.sort(key = lambda fname: file_size('books/'+fname))

# Matrix column names
columns = ['Books'] + book_names

# Similarity matrix
matrix = [columns]

# Iterate over pairs of books, filling out the matrix
for book_name in book_names:

  book_compressed_size = stats['single_book_compression_sizes'][book_name]['lzma']
  
  try:

      row = [book_name]
      
      for other_book_name in book_names:
        
        if other_book_name in stats['book_pair_compression_sizes'][book_name]:
          pair_compression_size = stats['book_pair_compression_sizes'][book_name][other_book_name]['lzma']
        elif book_name in stats['book_pair_compression_sizes'][other_book_name]:
          pair_compression_size = stats['book_pair_compression_sizes'][other_book_name][book_name]['lzma']
        else:
          raise Exception(book_name + ', ' + other_book_name)
          
        other_book_compressed_size = stats['single_book_compression_sizes'][other_book_name]['lzma']
        
        additional_information = (pair_compression_size - book_compressed_size) / other_book_compressed_size
        similarity = 1 - additional_information
        
        row.append(similarity)
    
  except KeyError: continue
  
  matrix.append(row)

"""

def median(l): l2=sorted(l); return l2[len(l2)//2]

def transpose(matrix):
  out = [[None]*len(matrix) for i in range(len(matrix[0]))]
  for i in range(len(matrix)):
    for j in range(len(matrix[0])):
      out[j][i] = matrix[i][j]
  return out


predictiveness = {bk_name: median([matrix[i][j] for j in range(1,len(matrix))]) for i,bk_name in enumerate(book_names,start=1)}
matrix[1:] = sorted(matrix[1:], key = lambda row: predictiveness[row[0]])

predictability = {bk_name: median([matrix[i][j] for i in range(1,len(matrix))]) for j,bk_name in enumerate(book_names,start=1)}
matrix = transpose(matrix)
matrix[1:] = sorted(matrix[1:], key = lambda row: predictability[row[0]])
matrix = transpose(matrix)

"""

matrix[1:] = matrix[1:][::-1]

# Save similarity data in CSV file
with open('similarity.csv','w+') as csv:
  for row in matrix:
    csv.write(','.join(map(str,row)) + '\n')