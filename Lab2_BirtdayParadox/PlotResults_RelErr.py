import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument('--ind_day', type=int, choices=[0,1,2], help='Index of the days: (0:365, 1:10**5, 2:10**6)', required=False, default=0)
# args = parser.parse_args()

#Load
possible_days = [365, 10**5, 10**6]
# number_days = possible_days[args.ind_day]

plt.figure(figsize=(12, 6), dpi=80)
colors = ['red','green','blue','grey']
for i,days in enumerate(possible_days):
	data = pd.read_csv(f'outputProb{days}.dat',sep='\t')


	Ns = np.array(data['persons'])
	n = max(Ns)

	rel_err = np.array(data['RelErr'])

	plt.plot(Ns,rel_err*100,c=colors[i], marker="o", label=f'Simulation with Runs: {days}')

title = 'Random Dropping Policy' if 0==1 else f'Random Load Balancing d: {0}'
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
