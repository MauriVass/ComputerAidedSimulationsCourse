import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

task = sys.argv[1]
is_exp_ser_time = sys.argv[2]
system_capacity = sys.argv[3]
number_services = sys.argv[4]

plt.figure(figsize=(12, 6), dpi=80)

for b in [5,10,15,20]: #tested with 3 runs
	print(b)
	data = pd.read_csv(f'queue{task}_{is_exp_ser_time}_B{b}.dat',sep='\t')

	x = np.array(data['LOAD'])
	y_theo = np.array(data['thWTime'])

	means = np.array(data['aveWT'])
	ci = data['ciWT']/2
	lb = means-ci
	ub = means+ci

	#Simulation
	plt.plot(x,means, marker="o", label=f'Simulation B={b}')
	plt.fill_between(x, lb, ub, alpha=0.2)
	label_lb = 'Theoretical Value'

	from matplotlib.font_manager import FontProperties
	fontP = FontProperties()
	fontP.set_size('x-small')
plt.fill_between([], [], [], color='gray', alpha=0.2, label=f'95% Confidence Interval')

# data = pd.read_csv(f'queuetime{task}_B{b}.dat',sep='\t')

# x = np.array(data['LOAD'])
# y_theo = np.array(data['thTime'])

# means = np.array(data['ave'])
# ci = data['ci']/2
# lb = means-ci
# ub = means+ci

# #Simulation
# plt.plot(x,means,c='red', marker="o", label='Simulation')
# plt.fill_between(x, lb, ub, color='green', alpha=0.2, label=f'95% Confidence Interval')
# label_lb = 'Theoretical Value'
# # plt.plot(x,y_theo, label=label_lb)

if(is_exp_ser_time=='True'):
	distribution = 'Exponential'
else:
	distribution = 'Uniform'

title = f'Queue System: {distribution} Distribution, Finite Queue, Single Server, 3 Runs'
plt.title(title)

plt.legend(loc='best', prop=fontP)#bbox_to_anchor=(1.05, 1)
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