import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

#Load
d = int(sys.argv[1])

files_index = [5,10, 20]
colors = ['red','green','blue','grey']
rel_errors = {}
for i in files_index:
	data = pd.read_csv(f'binsballs{d}_runs{i}.dat',sep='\t')


	Ns = list(data['n'])
	n = max(Ns)

	rel_err = np.array(data['RelErr'])
	#rel_errors.append(rel_err)
	rel_errors[i] = rel_err

plt.figure(figsize=(12, 6), dpi=80)
for i, index in enumerate(files_index):
	plt.plot(Ns,rel_errors[index]*100,c=colors[i], marker="o", label=f'Simulation with runs= {index}')

title = 'Random Dropping Policy' if d==1 else f'Random Load Balancing d = {d}'
plt.title(f'{title}')

plt.legend(loc='upper right')
plt.xscale("log")
plt.xlabel('Bins/Balls')
plt.ylabel('Relative Error (%)')
	
save_title = f'Images/{title}'.replace(' ','')
plt.savefig(save_title)
plt.show()
