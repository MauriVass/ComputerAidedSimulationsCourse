import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

data = pd.read_csv(f'queuesystem1_queuetime.dat',sep='\t')


x = np.array(data['LOAD'])
y_theo = np.array(data['thTime'])


means = np.array(data['ave'])
ci = data['ci']/2
lb = means-ci
ub = means+ci

plt.figure(figsize=(12, 6), dpi=80)
label_lb = 'Theoretical Value'
plt.plot(x,y_theo, label=label_lb)
#Simulation
plt.plot(x,means,c='red', marker="o", label='Simulation')
plt.fill_between(x, lb, ub, color='green', alpha=0.2, label=f'95% Confidence Interval')
#print(Ns)
#print(means)

title = f'Queue System: Exponential Distribution, Finite Queue, Single Server, 4 Runs'
plt.title(title)

plt.legend(loc='upper left')
#plt.xscale("log")
plt.xlabel('Load')
plt.ylabel('Queue Delay [s]')

remove_chars = [' ' , '=' , ',' , ':']
for r in remove_chars:
	title = title.replace(r,'')
print(title)
save_title = (f'Images/{title}')
plt.savefig(save_title)

plt.show()