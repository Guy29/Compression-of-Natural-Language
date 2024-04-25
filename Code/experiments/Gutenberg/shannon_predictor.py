from random      import randbytes
from codes       import Huffman, Arithmetic
from predictors  import Predictor, NGramPredictor, Compressor

if __name__ == "__main__":

    war_and_peace = open('../../../Data/books/pg2600.txt','rb+').read()

    war_and_peace_predictor = NGramPredictor(war_and_peace, window=6)
    war_and_peace_compressor = Compressor(predictor = war_and_peace_predictor, Code = Arithmetic)

    inigo_text     = b'Hello. My name is Inigo Montoya. You killed my father. Prepare to die.'
    inigo_encoding = war_and_peace_compressor.encode(inigo_text)
    inigo_decoding = war_and_peace_compressor.decode(inigo_encoding)

    print(len(inigo_encoding), inigo_encoding.hex())
    print(len(inigo_decoding), inigo_decoding)


    #############################################################


    print('\nThe predictor trained on War and Peace generates the ' +\
          'following example completion for the word "Nicholas":')
          
    print(war_and_peace_compressor.decode(randbytes(50)+b'\0', context=b'Nicholas').decode('utf8').__repr__())


    #############################################################

    # Use the predictor trained on War and Peace to compress
    #   various texts

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

    chosen_books = {}

    text_fnames = list(chosen_books.keys())
    book_titles = list(chosen_books.values())
    compression_ratios = []

    huffman_compressor   = Compressor(predictor = war_and_peace_predictor, Code = Huffman)
    arithmetic_compressor = war_and_peace_compressor

    for text_fname in text_fnames:
      current_text = open('../../../Data/books/'+text_fname,'rb+').read()
      
      huffman_compressed_text    = huffman_compressor.encode(current_text)
      huffman_compression_ratio  = len(current_text) / len(huffman_compressed_text)
      
      arithmetic_compressed_text = arithmetic_compressor.encode(current_text)
      arithmetic_compression_ratio  = len(current_text) / len(arithmetic_compressed_text)
      
      compression_ratios.append([huffman_compression_ratio, arithmetic_compression_ratio])
      
    import pandas as pd

    columns = ['Huffman compression size', 'Arithmetic compression size']
    WP_performance = pd.DataFrame(columns = columns, index = book_titles, data = compression_ratios)

    print(WP_performance)