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

Ns = list(data['n'])
n = max(Ns)
x = np.arange(min(Ns),n)
if(d==1):
    func = np.vectorize(functionNoLoad)
    y_lb = func(x)
    y_ub = 3 * y_lb
else:
    func = np.vectorize(functionLoad)
    y_lb = func(x,d)


means = list(data['ave'])
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

plt.legend(loc='lower right')
plt.xscale("log")
plt.xlabel('Bins/Balls')
plt.ylabel('Max Bin Occupacy')

save_title = (f'../Report/Images/Lab1/{title}Runs= {runs}').replace('=','').replace(' ','')
plt.savefig(save_title)
plt.show()
