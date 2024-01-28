class Codec:
  def __init__(self, encoder, decoder):
    self.encode = encoder
    self.decode = decoder

  def evaluate_on(self, original):
    encoded = self.encode(original)
    decoded = self.decode(encoded)
    correct = (decoded == original)
    compression_ratio = len(encoded) / len(original)
    return (correct, compression_ratio)

text = open('arthur-conan-doyle_the-adventures-of-sherlock-holmes.txt','rb+').read()

compression_methods = {}

# ---------------------------

compression_methods['No compression'] = Codec(lambda x: x, lambda x: x)

# ---------------------------

import zipfile
import io

def zipper(compression_method):
    def zip_(input_bytes):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'a', compression_method, compresslevel=9) as zip_file:
            zip_file.writestr('compressed.bin', input_bytes)

        return zip_buffer.getvalue()
        
    return zip_

def unzip_(compressed_data):
    zip_buffer = io.BytesIO(compressed_data)

    with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
        with zip_file.open('compressed.bin') as file:
            return file.read()



compression_methods['DEFLATE'] = Codec(zipper(zipfile.ZIP_DEFLATED), unzip_)
compression_methods['bzip2']   = Codec(zipper(zipfile.ZIP_BZIP2), unzip_)
compression_methods['LZMA']    = Codec(zipper(zipfile.ZIP_LZMA), unzip_)

# ---------------------------

import zlib, lzma, gzip
compression_methods['lzma_lib'] = Codec(lzma.compress, lzma.decompress)
compression_methods['zlib_lib'] = Codec(zlib.compress, zlib.decompress)
compression_methods['gzip_lib'] = Codec(gzip.compress, gzip.decompress)

# ---------------------------

import pandas as pd

rows = [(method_name, *method.evaluate_on(text)) for method_name, method in compression_methods.items()]
rows.sort(key = lambda r: r[2])

df = pd.DataFrame(rows, columns=['Method', 'Lossless', 'Ratio'])

print(df.to_string(index=False))