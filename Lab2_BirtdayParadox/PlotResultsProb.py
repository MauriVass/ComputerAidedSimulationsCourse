import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys

#Probability of conflict given a number off person and the number of days
def function(pers):
    return 1 - math.exp(-pers**2/(2*days))

days = int(sys.argv[1])
runs = 750
data = pd.read_csv(f'outputProb{days}.dat',sep='\t')

Ns = list(data['persons'])
n = max(Ns)
x = np.arange(min(Ns),n+1)

func = np.vectorize(function)
y = func(x)


means = list(data['ave'])
lb = np.array(data['ciLow'])
ub = np.array(data['ciHigh'])
CIs = ub-lb

plt.figure(figsize=(12, 6), dpi=80)
plt.plot(x,y,label='Theoretical Value')

plt.plot(Ns,means,c='red', marker="o",  label='Result Simulation')
plt.fill_between(Ns, lb, ub, color='gray', alpha=0.6, label='Confidence Interval')
plt.legend(loc='lower right')
#plt.xscale("log")
plt.xlabel('Number Persons')
plt.ylabel('Probability Conflict')
title = f'Probability Conflict: Days= {days} and Runs= {runs}'
plt.title(title)

save_title = (f'../Report/Images/Lab2/{title}').replace('=','').replace(' ','').replace(':','')
plt.savefig(save_title)
plt.show()
