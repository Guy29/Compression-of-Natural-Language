import os
import pandas      as pd
from   math        import log
from   functools   import cache
from   collections import Counter
from   statistics  import median


def entropy(symbol_frequencies):
  return sum(freq*log(freq,2) for freq in symbol_frequencies.values())


@cache
def n_gram_entropy(text, n):
  symbol_counts = Counter(text[i:i+n] for i in range(len(text)-n+1))
  total_count = symbol_counts.total()
  symbol_frequencies = {symbol: count/total_count for symbol,count in symbol_counts.items()}
  return -entropy(symbol_frequencies)


@cache
def marginal_entropy(text, n):
  return n_gram_entropy(text, n) - n_gram_entropy(text, n-1)



#############################################################

texts = []

for book_filename in os.listdir('../../Data/books'):
  if not book_filename.startswith('pg'): continue
  with open('../../Data/books/'+book_filename,'rb+') as book:
    text = book.read()
    if not b'Language: English' in text: continue
    texts.append(text)

text = b' '.join(texts)


table = [(n, n_gram_entropy(text,n), marginal_entropy(text,n)) for n in range(1,11)]
df    = pd.DataFrame(table, columns=['N', 'N-gram entropy', 'Marginal entropy'])
print(df.to_string(index=False))


print()


words = text.split()

table = [(n, n_gram_entropy(tuple(words),n), marginal_entropy(tuple(words),n)) for n in range(1,11)]
df    = pd.DataFrame(table, columns=['N', 'N-gram entropy', 'Marginal entropy'])
print(df.to_string(index=False))


#############################################################



import pylab

word_counts      = Counter(words)
total_word_count = word_counts.total()
word_frequencies = [count/total_word_count for word,count in word_counts.most_common(5000)]

c_estimates = [freq*index for freq,index in enumerate(word_frequencies,start=1)]
c           = median(c_estimates)

print(f"\nEstimate for constant in Zipf's law: {c}")

pylab.plot(range(1,len(word_frequencies)+1), word_frequencies)
pylab.plot(range(1,len(word_frequencies)+1), [c/i for i in range(1,len(word_frequencies)+1)])
pylab.grid(True)
pylab.xscale('log')
pylab.yscale('log')
pylab.xlabel('Word rank')
pylab.ylabel('Word probability')
pylab.savefig('zipf.png', dpi=150, bbox_inches='tight', pad_inches=0)