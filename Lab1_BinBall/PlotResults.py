import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

def functionNoLoad(x):
    return math.log(x)/(math.log(math.log(x)))
def functionLoad(x,d):
    return (math.log(math.log(x)))/math.log(d)

#Load
d = int(sys.argv[1])
runs = int(sys.argv[2])

data = pd.read_csv(f'binsballs{d}_runs{runs}.dat',sep='\t')

Ns = np.array(data['n'])
n = max(Ns)
x = np.arange(min(Ns),n)
if(d==1):
    func = np.vectorize(functionNoLoad)
    y_lb = func(x)
    y_ub = 3 * y_lb
else:
    func = np.vectorize(functionLoad)
    y_lb = func(x,d)


means = np.array(data['ave'])
lb = np.array(data['ciLow'])
ub = np.array(data['ciHigh'])
CIs = ub-lb

plt.figure(figsize=(12, 6), dpi=80)
#Upper bound
if(d==1):
    plt.plot(x,y_ub, label='Upper Theoretical Value')
#Lower Bound
label_lb = 'Lower Theoretical Value' if d==1 else 'Theoretical Value'
plt.plot(x,y_lb, label=label_lb)
#Simulation
plt.plot(Ns,means,c='red', marker="o", label='Simulation')
plt.fill_between(Ns, lb, ub, color='green', alpha=0.2, label=f'95% Confidence Interval')


title = 'Random Dropping Policy' if d==1 else f'Random Load Balancing d = {d}'
plt.title(f'{title}, Runs= {runs}')

plt.legend(loc='upper left')
plt.xscale("log")
plt.xlabel('Bins/Balls')
plt.ylabel('Max Bin Occupacy')
if(d>1):
	plt.ylim(0.8, 5.2)

remove_chars = [' ','=']
for r in remove_chars:
	title = title.replace(r,'')
save_title = (f'Images/{title}Runs= {runs}')
plt.savefig(save_title)
plt.show()
