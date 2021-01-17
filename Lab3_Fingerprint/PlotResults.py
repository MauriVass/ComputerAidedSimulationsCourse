import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

#Load
data_struc_type = int(sys.argv[1])
if(data_struc_type==0):
	data = pd.read_csv(f'bit_string_array_results.dat',sep='\t')
else:
	data = pd.read_csv(f'bloom_filters_results.dat',sep='\t')

number_words = 370103
plt.figure(figsize=(12, 6), dpi=80)

Ns = np.array(data['nbits'])
if(data_struc_type == 0):
	pb_fp = np.array(data['probFP'])
	plt.plot(Ns,pb_fp,c='red', marker="o", label='Simulation')
	title = f'Bit String Array Probability False Positive'
else:
	means = np.array(data['ave'])
	lb = np.clip(data['ciLow'],0,1)
	ub = np.clip(data['ciHigh'],0,1)

	y = data['thProbFP']
	plt.plot(Ns,y, label='Theoretical')

	plt.plot(Ns,means,c='red', marker="o", label='Simulation')
	plt.fill_between(Ns, lb, ub, color='green', alpha=0.2, label=f'95% Confidence Interval')
	title = f'Bloom Filter Probability False Positive'

plt.title(title)

plt.legend(loc='upper right')
plt.xlabel('Num bits')
plt.ylabel('Probability False Positive')

remove_chars = [' ','=',',']
for r in remove_chars:
	title = title.replace(r,'')
save_title = (f'Images/{title}')
plt.savefig(save_title)

plt.show()