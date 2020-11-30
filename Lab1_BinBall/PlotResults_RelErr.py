import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

#Load
d = int(sys.argv[1])

files_index = [3,5,10]
colors = ['red','green','blue','grey']
rel_errors = {}
for i in files_index:
	data = pd.read_csv(f'binsballs{d}_runs{i}.dat',sep='\t')


	Ns = np.array(data['n'])
	n = max(Ns)

	rel_err = np.array(data['RelErr'])
	#rel_errors.append(rel_err)
	rel_errors[i] = rel_err

plt.figure(figsize=(12, 6), dpi=80)
for i, index in enumerate(files_index):
	plt.plot(Ns,rel_errors[index]*100,c=colors[i], marker="o", label=f'Simulation with runs= {index}')

title = 'Random Dropping Policy' if d==1 else f'Random Load Balancing d = {d}'
title = 'Relative Errors: ' + title
plt.title(f'{title}')

plt.legend(loc='upper right')
plt.xscale("log")
plt.xlabel('Bins/Balls')
plt.ylabel('Relative Error (%)')

remove_chars = [' ',':','=']
for r in remove_chars:
	title = title.replace(r,'')
save_title = f'Images/{title}'
plt.savefig(save_title)
plt.show()
