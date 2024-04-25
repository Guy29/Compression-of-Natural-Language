import pandas      as     pd
from   random      import randbytes
from   codes       import Huffman, Arithmetic
from   predictors  import Predictor, LSTMPredictor, Compressor

#############################################################

# Setting up a predictor trained on War and peace

war_and_peace_predictor  = LSTMPredictor(None, window=6)
war_and_peace_predictor.load('test-lstm-10')
war_and_peace_compressor = Compressor(predictor = war_and_peace_predictor, Code = Arithmetic)

#############################################################

# Encoding-decoding test

inigo_text     = b'Hello. My name is Inigo Montoya. You killed my father. Prepare to die.'
inigo_encoding = war_and_peace_compressor.encode(inigo_text)
inigo_decoding = war_and_peace_compressor.decode(inigo_encoding)

print(f'Original text: {inigo_text}')
print(f'Encoded text : {inigo_encoding.hex()}')
print(f'Decoded text : {inigo_decoding}')
