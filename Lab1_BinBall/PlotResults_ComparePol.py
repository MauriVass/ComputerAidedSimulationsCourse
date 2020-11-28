import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

#Load
runs = int(sys.argv[1])

colors = ['red','green','blue']
plt.figure(figsize=(12, 6), dpi=80)
for i,d in enumerate([1,2,4]):
	data = pd.read_csv(f'binsballs{d}_runs{runs}.dat',sep='\t')

	Ns = list(data['n'])

	means = list(data['ave'])
	lb = np.array(data['ciLow'])
	ub = np.array(data['ciHigh'])
	CIs = ub-lb

	#Simulation
	lab = 'Random Dropping Policy' if d==1 else f'Load Random Balancing Policy d= {d}'
	plt.plot(Ns,means,c=colors[i], marker="o", label=lab)
	plt.fill_between(Ns, lb, ub, color=colors[i], alpha=0.2)

	title = 'Comparison among policies'
	plt.title(f'{title}, Runs= {runs}')

	plt.legend(loc='upper left')
	plt.xscale("log")
	plt.xlabel('Bins/Balls')
	plt.ylabel('Max Bin Occupacy')

save_title = (f'Images/{title}').replace(' ','')
plt.savefig(save_title)
plt.show()
