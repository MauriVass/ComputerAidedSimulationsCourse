import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

#Load
bloom_filter = int(sys.argv[1])
data = pd.read_csv(f'bit_string_array{bloom_filter}.dat',sep='\t')

number_words = 370103
Ns = np.array(data['nbits'])
y_theo = np.array(data['theoreticalProb'])
# n = max(Ns)
# x = np.arange(min(Ns),n+1)
# if(bloom_filter==0):
# 	y = number_words/(2**x)
# else:
# 	num_hashes = np.array(data['nHashes'])[0]
# 	#print(num_hashes)
# 	#print(x)
# 	y = [ (1-math.exp(-num_hashes*number_words/2**v))**num_hashes for v in x]

means = np.array(data['ave'])
lb = np.clip(data['ciLow'],0,1)
ub = np.clip(data['ciHigh'],0,1)

plt.figure(figsize=(12, 6), dpi=80)
label_lb = 'Theoretical Value'
plt.plot(Ns,y_theo, label=label_lb)
#Simulation
plt.plot(Ns,means,c='red', marker="o", label='Simulation')
plt.fill_between(Ns, lb, ub, color='green', alpha=0.2, label=f'95% Confidence Interval')
#print(Ns)
#print(means)

if(bloom_filter == 0):
	title = f'Bit String Array Probability False Positive'
else:
	title = f'Bloom Filter Probability False Positive'
title += f', Runs {5}'
plt.title(title)

plt.legend(loc='upper right')
#plt.xscale("log")
plt.xlabel('Num bits')
plt.ylabel('Probability False Positive')

remove_chars = [' ','=',',']
for r in remove_chars:
	title = title.replace(r,'')
save_title = (f'Images/{title}')
plt.savefig(save_title)

plt.show()