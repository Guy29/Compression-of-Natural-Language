import os, zipfile, lzma, json
from co_compressor import *

def read_txt_from_zip(zip_filename):
    # Remove the .zip extension and prepare the target .txt filename
    base_name = zip_filename.split('/')[-1].split('.')[0]
    target_txt_filename = base_name + '.txt'
    
    # Initialize variable to store the contents
    file_contents = None

    # Use 'with' statement to ensure the zip file is properly closed after processing
    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        # Check if the target .txt file exists in the zip archive
        if target_txt_filename in zip_ref.namelist():
            # Read the target .txt file contents as bytes directly from the archive
            with zip_ref.open(target_txt_filename, 'r') as file:
                file_contents = file.read()
        else:
            # If the file is not found, you might want to handle this case, e.g., by raising an exception
            raise FileNotFoundError(f"{target_txt_filename} does not exist in the zip archive.")

    # Return the contents of the .txt file as bytes
    return file_contents

k = os.listdir('../../../Data/book_zips/')

with open('stats.json') as f:
    stats = json.load(f)
    self_compression_stats = stats['self_compression']

best_compression_fname = max(self_compression_stats, key=lambda k: self_compression_stats[k])
best_compression_ratio = self_compression_stats[best_compression_fname]

for fname in k:
  
  if '(' in fname: continue
  if not fname.endswith('.zip'): continue
  if fname in self_compression_stats: continue
  if fname in ['3513.zip', '3514.zip']: continue
  
  try:
    text = read_txt_from_zip('../../../Data/book_zips/'+fname)
  except FileNotFoundError:
    continue
  book_name = text.split(b'\r')[0].split(b'eBook of ')[-1]
  if b'Human Genome Project' in book_name: continue
  
  compressed_size = len(lzma.compress(text))
  compressor = CoCompressor(text)
  cocompressed_size = len(compressor.compress(text))
  compression_ratio = compressed_size / cocompressed_size
  
  self_compression_stats[fname] = compression_ratio
  
  if compression_ratio > best_compression_ratio:
    best_compression_fname = fname
    best_compression_ratio = compression_ratio
    print(best_compression_fname, best_compression_ratio, book_name)
  
  if len(self_compression_stats)%20==0:
    stats['self_compression'] = self_compression_stats
    with open('stats.json','w+') as f:
      json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f'{len(self_compression_stats)} entries saved.')