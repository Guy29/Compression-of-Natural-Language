import matplotlib.pyplot as plt
import numpy as np
from shannon_predictor import *
from collections import Counter
import pandas as pd



war_and_peace = open('../../../Data/books/pg2600.txt','rb').read()
war_and_peace_predictor = Predictor(war_and_peace, window=6)

sherlock_text   = b'To Sherlock Holmes she is always the woman. I have seldom heard him mention her under any other name. In his eyes she eclipses and predominates the whole of her sex. It was not that he felt any emotion akin to love for Irene Adler.'
sherlock_string = sherlock_text.decode()

symbols, probabilities, ranks = war_and_peace_predictor.encoding_probabilities_ranks(sherlock_text)

cmap = plt.get_cmap("cividis")

# Create figure and axis with a space for a colorbar
fig, (ax, cax) = plt.subplots(nrows=2, gridspec_kw={"height_ratios": [10, 1]}, figsize=(10, 4))

# Turn off axis for the main plot
ax.axis('off')

# Define the maximum number of characters per line and the initial position
max_chars_per_line = 50
row_height         = 0.17
line_height        = 0.15

# Process text by lines
num_lines = (len(sherlock_string) // max_chars_per_line) + 1

for line in range(num_lines):
    start     = line  * max_chars_per_line
    end       = start + max_chars_per_line
    line_text = sherlock_string[start:end]
    
    # Display each character in the line
    for i, char in enumerate(line_text):
        color = cmap(probabilities[start + i])
        
        ax.text(i * 0.02, 1 - line * row_height * 2, char, color='white', fontsize=14, fontname='monospace',
                bbox=dict(facecolor=color, edgecolor=color, pad=0.2, boxstyle='square'))
        
        ax.text(i * 0.02, 1 - line_height - line * row_height * 2, str(ranks[start+i]), color='black', fontsize=7, fontname='monospace',
                bbox=dict(facecolor='white', edgecolor='black', pad=0.5, boxstyle='square'))

# Create a colorbar in the extra axes space provided
sm   = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=0, vmax=1))
cbar = plt.colorbar(sm, cax=cax, orientation='horizontal')
cbar.set_label('Prior probability of symbol')

plt.tight_layout()
plt.savefig('predictor_surprisal_by_char.png', dpi=300, bbox_inches='tight', pad_inches=0)
plt.close()


#############################################################


full_sherlock = open('../../../Data/books/pg1661.txt','rb').read()

symbols, probabilities, ranks = war_and_peace_predictor.encoding_probabilities_ranks(full_sherlock)
rank_frequencies   = Counter(ranks)
rank_probabilities = Counter({r:rank_frequencies[r]/len(symbols) for r in rank_frequencies})

df = pd.DataFrame(columns = ['1','2','3','4','5'], index = ['Rank','Probability'],
                  data = [range(1,6), [rank_probabilities[r] for r in range(1,6)]])

print(df)

highest_shown_rank = 30
bin_edges = [i-0.5 for i in range(1,highest_shown_rank+2)]

plt.hist(range(1,highest_shown_rank+1),
         weights=[rank_probabilities[i] for i in range(1,highest_shown_rank+1)],
         bins=bin_edges,
         color='#49cd49', edgecolor='white', linewidth=1)

plt.plot(bin_edges, [1/(i*i) for i in bin_edges], color='black', linestyle='--')
plt.xlim((0.5,highest_shown_rank+0.5))
plt.xticks([1,5,10,15,20,25,30])
plt.ylim((0.0001,1))
plt.yscale('log')
plt.savefig('predictor_surprisal_histogram.png', dpi=300, bbox_inches='tight', pad_inches=0)