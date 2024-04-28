import sys
sys.path.insert(0, '../libraries')

import pandas      as     pd
from   random      import randbytes
from   codes       import Huffman, Arithmetic
from   predictors  import Predictor, NGramPredictor, Compressor
import time

#############################################################

# Setting up a Predictor trained on War and Peace and the corresponding Compressor

war_and_peace_text       = open('../../Data/books/pg2600.txt','rb+').read()
war_and_peace_predictor  = NGramPredictor(war_and_peace_text, window=6)
war_and_peace_compressor = Compressor(predictor = war_and_peace_predictor, Code = Arithmetic)

#############################################################

# Encoding-decoding test

inigo_text     = b'Hello. My name is Inigo Montoya. You killed my father. Prepare to die.'
inigo_encoding = war_and_peace_compressor.encode(inigo_text)
inigo_decoding = war_and_peace_compressor.decode(inigo_encoding)

print(f'Original text: {inigo_text}')
print(f'Encoded text : {inigo_encoding.hex()}')
print(f'Decoded text : {inigo_decoding}')

#############################################################

# Decoding noise to generate completions

print('\nThe predictor trained on War and Peace generates the following example completion for the word "Nicholas":')
print(war_and_peace_compressor.decode(randbytes(50)+b'\0', context=b'Nicholas').decode('utf8').__repr__())

#############################################################

# Use the predictor trained on War and Peace to compress various texts and make a comparison table

chosen_books = {
    "pg10.txt": "The King James Version of the Bible",
    "pg100.txt": "The Complete Works of William Shakespeare",
    "pg11.txt": "Alice's Adventures in Wonderland",
    "pg1184.txt": "The Count of Monte Cristo",
    "pg145.txt": "Middlemarch",
    "pg996.txt": "Don Quixote",
    "pg2554.txt": "Crime and Punishment",
    "pg2600.txt": "War and Peace",
}

WP_performance  = pd.DataFrame()

compressors = [Compressor(predictor = war_and_peace_predictor, Code = Arithmetic),
               Compressor(predictor = war_and_peace_predictor, Code = Huffman)]

while compressors:

  compressor = compressors.pop()

  for text_fname, text_title in chosen_books.items():
  
    current_text         = open('../../Data/books/'+text_fname,'rb+').read()
    compressed_text      = compressor.encode(current_text, memoize=0.5)
    compression_ratio    = len(current_text) / len(compressed_text)
      
    WP_performance.at[text_title, f'{compressor.Code.name} compression size'] = compression_ratio
    
  del compressor

print()
print(WP_performance)