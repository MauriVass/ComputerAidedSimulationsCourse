import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

def theoreticalFormula(x):
	return (1-math.exp(-x*number_words/storage_length))**x

plt.figure(figsize=(12, 6), dpi=80)

number_words = 370103
#Divide the elements in split to have a better visualization
min_split = 0
max_split = 6
possible_num_bits = [19, 20, 21, 22, 23, 24]
min_theo = {}
colors = [(1,0,0),(0,1,0),(0,0,1),(1,0.5,0),(1,0,1),(0,1,1)]
for i,num_bits in enumerate(possible_num_bits[min_split:max_split]):
	storage_length = 2**num_bits
	k_theo = storage_length/number_words*math.log(2)
	min_theo[k_theo] = theoreticalFormula(k_theo) 
	y = {}
	for k in  range(1,33):
		prob = theoreticalFormula(k)
		y[k] = prob
	plt.plot(list(y.keys()),list(y.values()),c=colors[min_split+i] ,marker="o", label=num_bits)
label_lb = 'Theoretical Value'

s = np.full(max_split-min_split,150)
print('K optimal values: ',list(min_theo.keys()))
plt.scatter(list(min_theo.keys()),list(min_theo.values()), c=list(colors)[min_split:max_split] ,marker="x",s=s,zorder=1,label='Minima')

title = f'Bloom Filters Probability False Positive'
plt.title(title)

plt.legend(loc='center right')
plt.xlabel('k')
plt.ylabel('Probability False Positive')

remove_chars = [' ']
for r in remove_chars:
	title = (title+f'{min_split}{max_split}').replace(r,'')
save_title = (f'Images/{title}q10')
plt.savefig(save_title)
plt.show()