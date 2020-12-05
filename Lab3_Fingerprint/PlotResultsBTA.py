import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

#Load
data = pd.read_csv(f'bit_string_array.dat',sep='\t')

Ns = np.array(data['nbits'])
n = max(Ns)
x = np.arange(min(Ns),n+1)
y = 370103/2**x

means = np.array(data['prob_FalsePos'])
#lb = np.clip(data['ciLow'],0,1)
#ub = np.clip(data['ciHigh'],0,1)

plt.figure(figsize=(12, 6), dpi=80)
label_lb = 'Theoretical Value'
#plt.plot(x,y, label=label_lb)
#Simulation
plt.plot(Ns,means,c='red', marker="o", label='Simulation')
#plt.fill_between(Ns, lb, ub, color='green', alpha=0.2, label=f'95% Confidence Interval')


title = f'Bit String Array Probability False Positive, Runs= {3}'
plt.title(title)

#plt.legend(loc='upper right')
#plt.xscale("log")
plt.xlabel('Num bits')
plt.ylabel('Probability False Positive')


remove_chars = [' ','=',',']
for r in remove_chars:
	title = title.replace(r,'')
save_title = (f'Images/{title}')
plt.savefig(save_title)

plt.show()