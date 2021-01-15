import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--ind_day', type=int, choices=[0,1,2], help='Index of the days: (0:365, 1:10**5, 2:10**6)', required=False, default=0)
parser.add_argument('--runs', type=int, help='Number or runs: (r>1)', required=False, default=3)
parser.add_argument('-relError', action='store_true')
args = parser.parse_args()

#Probability of conflict given a number of person and the number of days
def function(pers):
    return 1 - math.exp(-pers**2/(2*days))

isRelErr = True if args.relError else False

index_day = args.ind_day
possible_days = [365, 10**5, 10**6]
days = possible_days[index_day]
runs = args.runs
data = pd.read_csv(f'outputProb{days}.dat',sep='\t')

Ns = np.array(data['persons'])
n = max(Ns)
x = np.arange(min(Ns),n+1)

func = np.vectorize(function)
y = func(x)

if(isRelErr):
	means = np.array(data['RelErr'])
else:
	means = np.array(data['ave'])
	lb = np.array(data['ciLow'])
	ub = np.array(data['ciHigh'])
	CIs = ub-lb

plt.figure(figsize=(12, 6), dpi=80)

if(isRelErr):
	plt.ylabel('Relative Error (%)')
	title = f'Relative Error: Days: {days}, Runs: {runs}'
else:
	plt.plot(x,y,label='Theoretical Value')
	plt.fill_between(Ns, lb, ub, color='green', alpha=0.2, label='Confidence Interval')
	plt.ylabel('Probability Conflict')
	title = f'Probability Conflict: Days: {days}, Runs: {runs}'

plt.plot(Ns,means,c='red', marker="o",  label='Result Simulation')
plt.xlabel('Number Persons')
plt.legend(loc='best')
plt.title(title)

remove_chars = [' ','=',':',',']
for r in remove_chars:
	title = title.replace(r,'')
save_title = (f'Images/{title}')
plt.savefig(save_title)
plt.show()
