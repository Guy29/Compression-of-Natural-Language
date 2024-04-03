import os
from lzma import compress

books_location = '../../../Data/books/'

targets = [books_location+filename for filename in os.listdir('books')]

# Function to return the size of a file given its name
def file_size(filename):
  with open(filename,'rb+') as f:
    return f.seek(0,2)

targets = filter(lambda fname: file_size(fname)<200000, targets)

targets = [open(fname,'rb+').read() for fname in targets]

def oracle(pred):
  return sum(len(compress(pred+body)) for body in targets)

pred = b'\x0b\n\x0b\x08\n\x08\tr!\xc0\xc0\xa3\xa3\xa3`"c!I\r*\r\x0c\r\x0bRjogwd>af;Uxywrhip.\xc0 \xef\x80\xa2@\xef*\xefA\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef\xef*ss8NNN\rBGNNT\x08\nB.N\x00\n\no"-\xc0\xc0\x00\nAA@p8\x0e\xefAl\x0e\x08\nM ilio\xef@TnAA\xef\xefAIb\x0e\nAlAU*tA\xefNt\x0co:\x08\x00t\x0fUi&i\x0eAToA:il\\A\xef\xbb[he!A" \rNA&I;Bo\rWE4h\\eAo[OfAti&i)""Sd\xef\xefd\xefAldb/UNA"t$ e hu,o\rt.`AhAuq\xefqe\rHAnqe\re\x08L\rdAqy:-cg\r\nf, \r\nAf\xef\xbb[TAe0 Izif\xeff[auqAA\xef\xef\x80\xef PfzAfs'
while True:
  best_i = -1
  best_score = 1e400
  for i in range(256):
    print(chr(8)*50 + f'{i}/256', end='', flush=True)
    temp_pred = pred + bytes([i])
    score = oracle(temp_pred)
    if score < best_score: best_score = score; best_i = i
  pred += bytes([best_i])
  print(chr(8)*50, best_score, ' ', pred, sep='')
  with open('predictor.bytes','wb+') as f:
    f.write(pred)