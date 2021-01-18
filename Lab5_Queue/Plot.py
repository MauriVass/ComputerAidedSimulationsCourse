import numpy as np
import scipy.stats as s
import math
import matplotlib.pyplot as plt
import pandas as pd
import sys
import seaborn as sns

import argparse
parser = argparse.ArgumentParser() 
parser.add_argument('--task', type=int, help='Number of task', choices=[1,2,3], required=False, default=1)
parser.add_argument('--servt', type=str, help='Service Time: [Exp, Uni]', choices=['Exp','Uni'], required=False, default='Exp')
parser.add_argument('--maxcap', type=int, help='Maximum system capacity (-1:np.inf)', required=False, default=-1)
parser.add_argument('--nserv', type=int, help='Number of services (>0)', required=False, default=1)
parser.add_argument('--servpoli', type=int, help='Server Policy', required=False, default=1)
args = parser.parse_args()

task = args.task
exp_service_time = True if args.servt=='Exp' else False
system_capacity = np.inf if args.maxcap==-1 else args.maxcap
number_services = args.nserv
policy = args.servpoli

#Some check to set the title correctly
distribution = 	'Exponential' 	if exp_service_time else		'Uniform'
queue_length = 	'Infinite' 		if system_capacity==np.inf else 'Finite'
servers = 		'Single' 		if number_services==1 else 		'Multi'

title = f'Queue System: {distribution} Distribution, {queue_length} Queue, {servers} Server, 3 Runs'

if(task==1):
	data = pd.read_csv(f'queue{task}_{exp_service_time}_B{system_capacity}_S{number_services}_P{policy}.dat',sep='\t')

	x = np.array(data['LOAD'])
	y_theo = np.array(data['thWT'])

	means = np.array(data['aveWT'])
	ci = data['ciWT']/2
	lb = means-ci
	ub = means+ci

	plt.figure(figsize=(12, 6), dpi=80)
	plt.plot(x,means,c='red', marker="o", label='Simulation')
	plt.fill_between(x, lb, ub, color='green', alpha=0.2, label=f'95% Confidence Interval')
	label_lb = 'Theoretical Value'
	plt.plot(x,y_theo, label=label_lb)

	plt.title(title)

	plt.legend(loc='best')
	plt.xlabel('Load')
	plt.ylabel('Queue Delay [s]')
	if(exp_service_time):
		plt.ylim(0,100) #It diverges for ro->1

	title = title.replace(' ','').replace(',','').replace(':','')
	save_title = (f'Images/{title}t{task}')
	plt.savefig(save_title)

	plt.show()

elif(task==2):
	fig1, ax1 = plt.subplots(figsize=(12, 6), dpi=80)
	fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=80)
	for b in [5,10,15,20]: #tested with 3 runs
		data = pd.read_csv(f'queue{task}_{exp_service_time}_B{b}_S{number_services}_P{policy}.dat',sep='\t')
		x = np.array(data['LOAD'])

		means = np.array(data['aveWT'])
		ci = data['ciWT']/2
		lb = means-ci
		ub = means+ci

		#Simulation
		ax1.plot(x,means, marker="o", label=f'Simulation B={b}')
		# plt.fill_between(x, lb, ub, alpha=0.2)
		ax1.set_title(title)
		ax1.legend(loc='best')
		ax1.set_xlabel('Load')
		ax1.set_ylabel('Queue Delay [s]')


		means = np.array(data['aveLoss'])
		ci = data['ciWT']/2
		lb = means-ci
		ub = means+ci

		ax2.plot(x,means, marker="o", label=f'Simulation B={b}')
		# plt.fill_between(x, lb, ub, alpha=0.2)
		ax2.set_title(title)
		ax2.legend(loc='best')
		ax2.set_xlabel('Load')
		ax2.set_ylabel('Client Loss Probability')

	title1 = title.replace(' ','').replace(',','').replace(':','')
	save_title1 = (f'Images/{title1}t{task}')
	fig1.savefig(save_title1)
	# plt.show()
	title = title.replace(' ','').replace(',','').replace(':','')
	save_title = (f'Images/{title}t{task}_probloss')
	fig2.savefig(save_title)
	plt.show()
elif(task==3):
	fig1, ax1 = plt.subplots(figsize=(12, 6), dpi=80)
	# fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=80)
	for m in [2,4,6,8,10,20]: #tested with 3 runs
		data = pd.read_csv(f'queue{task}_{exp_service_time}_B{system_capacity}_S{m}_P{policy}.dat',sep='\t')
		x = np.array(data['LOAD'])

		means = np.array(data['aveWT'])
		ci = data['ciWT']/2
		lb = means-ci
		ub = means+ci

		#Simulation
		ax1.plot(x,means, marker="o", label=f'Simulation m={m}')
		# plt.fill_between(x, lb, ub, alpha=0.2)
		ax1.set_title(title)
		ax1.legend(loc='best')
		ax1.set_xlabel('Load')
		ax1.set_ylabel('Queue Delay [s]')
		#For better visualization
		ax1.set_ylim(-1,20)

	title = title.replace(' ','').replace(',','').replace(':','')
	save_title = (f'Images/{title}t{task}')
	fig1.savefig(save_title)
	plt.show()

		# prob_losses = 'aveLoss'
		# means = np.array(data[prob_losses])
		# ci = data[prob_losses]/2
		# lb = means-ci
		# ub = means+ci

		# ax2.plot(x,means, label=f'Simulation B={b}')
		# ax2.set_title(title)
		# ax2.legend(loc='best')
		# ax2.set_xlabel('Load')
		# ax2.set_ylabel('Client Loss Probability')

		# # plt.show()
		# title = title.replace(' ','').replace(',','')
		# save_title = (f'Images/{title}')
		# fig2.savefig(save_title)
	# plt.fill_between([], [], [], color='gray', alpha=0.2, label=f'95% Confidence Interval')


