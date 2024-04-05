from collections import defaultdict
import matplotlib.pyplot as plt

with open('practical-out.txt') as f:
  t = [line.split(',') for line in f.readlines()]

def f(): return defaultdict(f)
data = f()
for bkfn1,bkfn2,bk1,bk2,i,c,k,koc in t:
  data[bk1][bk2] = float(koc)

for title in data:
  data[title] = sorted(list(data[title].values()), reverse=True)

# Plotting
plt.figure(figsize=(10, 6))
for title, lst in data.items():
    plt.plot(lst, label=title)

#plt.yscale('log')
# Explicitly setting y-axis ticks for the log scale
plt.yticks([0.9,1,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2], ['0.9','1','1.1','1.2','1.3','1.4','1.5','1.6','1.7','1.8','1.9','2'])

# Removing x-axis ticks and vertical grid lines
plt.xticks([])
plt.grid(axis='y', linestyle='--')

# Setting x-axis limits
plt.xlim(2, 96)
plt.ylim(0.9, 1.3)

plt.legend()
plt.xlabel('Index')
plt.ylabel('Value (log scale)')
plt.title('Sorted Lists on Log Scale')

plt.show()
