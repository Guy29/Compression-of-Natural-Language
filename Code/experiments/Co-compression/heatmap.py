import json
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# Load book compression stats
with open('stats.json','r') as f:
  stats = json.load(f)


# Load the CSV file
file_path = 'similarity.csv'
similarity_matrix = pd.read_csv(file_path, index_col=0)


# Get a dict copy of the data
similarity_dict = similarity_matrix.to_dict()
  

# Put all similarity scores into one list
all_scores = []
for bk_name1 in similarity_dict:
  for bk_name2 in similarity_dict[bk_name1]:
    all_scores.append((similarity_dict[bk_name1][bk_name2],bk_name1,bk_name2))


# Sort that list so that most similar pairs of books come first
all_scores.sort()


# Filter out pairs where a book is being compared with itself
different_book_scores = [(score,bk1,bk2) for (score,bk1,bk2) in all_scores if bk1!=bk2]


# Function to print human-friendly book names instead of Gutenberg filenames
def title(book_filename):
  return f"{stats['book_titles'][book_filename]} ({book_filename})"


# Get the top and bottom pairs of books and replace book file names with book titles
top = [(score,title(bk1),title(bk2)) for (score,bk1,bk2) in different_book_scores[:10]]
bottom = [(score,title(bk1),title(bk2)) for (score,bk1,bk2) in different_book_scores[-10:]]


# Display them
df = pd.DataFrame(top + [('...',)*3] + bottom, columns=['Score', 'Book 1', 'Book 2'])
print(df.to_string(index=False))

# Rename the columns in rows in the matrix from book filenames to the corresponding abbreviated book titles
similarity_matrix = similarity_matrix.rename(columns=stats['abbreviated_book_titles'], index=stats['abbreviated_book_titles'])

# Creating the heatmap
plt.figure(figsize=(20, 15))
heatmap = sns.heatmap(similarity_matrix, cmap='viridis')
plt.title('Book Similarity', fontsize=20)
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.show()
#plt.savefig('fig_2.png')