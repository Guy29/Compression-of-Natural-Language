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

for fname in k[:0]:
  
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



with open('stats.json','r+') as f:
  stats = json.load(f)

items = stats['self_compression'].items()
vals = stats['self_compression'].values()

print(f'There are {len(vals)} texts considered in the dataset.')
print(f'Of which {len([v for v in vals if v>1095.4])} have a better RCR than Middlemarch.')

better_performing = [filename for (filename,val) in items if val>1095.4]

def get_title_from_filename(fname):
  return read_txt_from_zip('../../../Data/book_zips/'+fname).split(b'\r')[0].split(b'EBook of ')[-1]

better_performing = [get_title_from_filename(fname) for fname in better_performing]
  

print(f'These are: {better_performing}')

import matplotlib.pyplot as plt

plt.hist(vals, bins=50, color='#49cd49', edgecolor='white', linewidth=1)
plt.yscale('log')
plt.xlim((0,1500))
plt.xlabel('Self-compression score')
plt.ylabel('Frequency (log scale)')
plt.savefig('fig_self-compression_histogram.png', dpi=150, bbox_inches='tight', pad_inches=0)



#for fname in [filename for (filename,val) in items if val>800]:
#  text = read_txt_from_zip('../../../Data/book_zips/'+fname)
#  with open('../../../Data/new_books/'+fname.split('.')[0]+'.txt','wb+') as f:
#    f.write(text)