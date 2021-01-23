import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--bins', type=int, help='Number of bins: [1,2,4]', required=False, default=1)
args = parser.parse_args()

#Load
d = args.bins

files_runs = [3,5,10]
colors = ['red','green','blue','grey']
plt.figure(figsize=(12, 6), dpi=80)
for i, index in enumerate(files_runs):
	data = pd.read_csv(f'binsballs_bins{d}_runs{index}.dat',sep='\t')

	Ns = np.array(data['n'])
	n = max(Ns)

	rel_err = np.array(data['RelErr'])

	plt.plot(Ns,rel_err*100,c=colors[i], marker="o", label=f'Simulation with Runs: {index}')

title = 'Random Dropping Policy' if d==1 else f'Random Load Balancing d: {d}'
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
