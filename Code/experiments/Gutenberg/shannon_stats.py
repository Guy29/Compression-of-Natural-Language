import os
import pandas as pd
from math        import log
from functools   import cache
from collections import Counter
from statistics  import median


def entropy(symbol_frequencies):
  return -sum(freq*log(freq,2) for freq in symbol_frequencies.values())


@cache
def n_gram_entropy(text, n):
  n_gram_counts = Counter(text[i:i+n] for i in range(len(text)-n+1))
  total_count = n_gram_counts.total()
  n_gram_frequencies = {n_gram: count/total_count for n_gram,count in n_gram_counts.items()}
  return entropy(n_gram_frequencies)


@cache
def marginal_entropy(text, n):
  return n_gram_entropy(text, n) - n_gram_entropy(text, n-1)



#############################################################

book_filenames = os.listdir('../../../Data/books')

text = []
for filename in book_filenames:
  with open('books/'+filename,'rb+') as book:
    text.append(book.read())

text = b''.join(text)

print(f'Text length: {len(text)} bytes\n')


table = [(n, n_gram_entropy(text,n), marginal_entropy(text,n)) for n in range(1,11)]
df    = pd.DataFrame(table, columns=['N', 'N-gram entropy', 'Marginal entropy'])
print(df.to_string(index=False))


print()


words = text.split()

table = [(n, n_gram_entropy(tuple(words),n), marginal_entropy(tuple(words),n)) for n in range(1,11)]
df    = pd.DataFrame(table, columns=['N', 'N-word entropy', 'Marginal entropy'])
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
pylab.show()


#############################################################

# Output

"""
Text length: 77955344

 N  N-gram entropy  Marginal entropy
 1        4.674789          4.674789
 2        8.193527          3.518738
 3       11.077931          2.884403
 4       13.430718          2.352787
 5       15.434333          2.003615
 6       17.216262          1.781929
 7       18.825973          1.609712
 8       20.264030          1.438057
 9       21.517189          1.253159
10       22.574182          1.056994

 N  N-word entropy  Marginal entropy
 1       11.477039         11.477039
 2       18.702746          7.225707
 3       22.187337          3.484592
 4       23.213621          1.026283
 5       23.434336          0.220715
 6       23.479111          0.044775
 7       23.491305          0.012193
 8       23.496988          0.005683
 9       23.500703          0.003715
10       23.503611          0.002908

Estimate for constant in Zipf's law: 0.08241309623762047
"""


#############################################################