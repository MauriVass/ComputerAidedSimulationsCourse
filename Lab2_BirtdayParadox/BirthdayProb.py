import numpy as np
import random
from scipy.stats import t
import sys
import math 

# initial settings
initial_seed = 2500
confidence_level = 0.95
runs = 180 # number of runs
#True -> find probability of conflict
#False -> find minimum number of people needed to experience a collision
isProb = False

#Index for the number of days required: 0:365, 1:10**5, 2:10**6
index_day = int(sys.argv[1])
possible_days = [365, 10**5, 10**6]
number_days = possible_days[index_day]

if(isProb):
	#Calculate lower and upper bounds using the theoretical formula
	people_lower_bound = int( math.sqrt(2*number_days*math.log(1/(1-0.05))) )#The lower bound is calculated with probability 0.1
	people_upper_bound = int( math.sqrt(2*number_days*math.log(1/(1-0.95))) )#The upper bound is calculated with probability 0.9
	#Use a number of points increasing with the number of days
	step = int((people_upper_bound - people_lower_bound) / 20 + 5*index_day)
	number_persons = range(people_lower_bound,people_upper_bound,step)

'''
#Use a fixed step
#Set different starting values and steps depending on the number of total days
if(number_days == possible_days[0]):
	number_persons = range(3,upper_bound,2)
elif(number_days == possible_days[1]):
	number_persons = range(100,upper_bound,20)
elif(number_days == possible_days[2]):
	number_persons = range(300,upper_bound,60)
'''

#Use uniform distribution
#number_persons = [ int(x*upper_bound) for x in sorted(np.random.uniform(0,1,size=40)) ]

#Print Input Parameters
print("*** INITIAL SETTINGS ***")
if(isProb):
	print("Goal: Find probability of conflict")
else:
	print("Goal: Find minimum number of people needed to experience a collision")
print("Birthday Paradox numbers for the simulation:")
print("Number of days ",number_days)
if(isProb):
	print("Number of persons ",number_persons)
print("Initial seed ",initial_seed)
print("Confidence level ",confidence_level)
print("Number of runs ",runs)
print("*** END INITIAL SETTINGS ***")

# function to compute confidence intervals
def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=runs - 1) # threshold for t_student

	if(isProb):
		ave = x # average. This is the total number of collision divided by the total number of persons
		stddev = x*(1-x) # std dev
		ci = t_sh * stddev / np.sqrt(runs) # confidence interval half width
	else:
		ave = x.mean() # average
		stddev = x.std(ddof=1) # std dev
		ci = t_sh * stddev / np.sqrt(runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave # if ave>0 else # relative error
	return ave, ci, rel_err

def run_simulator(pers): # run the birthday paradox model
	random.seed(a=initial_seed) # reset initial seed
	confli_value = 0 
	#This case is for the minimum value case
	number_people_conf = np.full(runs, 0)
	for r in range(runs): # for each run
		# birthday[i] is:
		#False: no person has a birtday on this day (yet),
		#True: at least one person
		birthday = np.full(number_days, False)

		#This variable is for the probability case
		number_conflicts = 0
		#This variable is for the minimun value case
		conflict_number = -1

		#The maximum number of iteration changes depending on the value of isProb
		#'number_days+1' means that we have 100% to experience a conflict
		max_value_iter = pers if isProb else number_days+1
		for i in range(max_value_iter): # for each person
			d = random.randrange(number_days) #get random day
			if(birthday[d]==True): #Conflict
				conflict_number = i
				break #Exit the for loop
			birthday[d]=True #No conflict, set birthday[d] to True

		if(conflict_number>0):#if this is > then 0 it means that a conflict accured
			confli_value += 1 # store the number of conflicts. This then will be divided by the total number of persons. Used for isProb=True
			number_people_conf[r] = conflict_number #Store the first time(minimun number) we experience a conflict. Used for isProb=False

	if(isProb):
		confli_value = confli_value / runs
		ave, ci, rel_err = evaluate_conf_interval(confli_value)
		return pers, ave - ci, ave, ave + ci, rel_err
	else:
		theoretic_value = math.sqrt(math.pi/2*number_days)
		ave, ci, rel_err = evaluate_conf_interval(number_people_conf)
		print(f'Simulated: {ave:.2f}, Theoretical: {theoretic_value:.2f}, Difference mean-theoretical: {(ave-theoretic_value):.2f}, CI: {(ci):.2f}')
		return ave - ci, ave, ave + ci, rel_err, theoretic_value

#########################
# main simulation engine
#########################
# open the outfile file and write the header
output_file = f"outputProb{number_days}.dat" if isProb else f"outputMin{number_days}.dat"
datafile = open(output_file, "w")
if(isProb):
	print("persons\tciLow\tave\tciHigh\tRelErr",file=datafile)
else:
	print("ciLow\tave\tciHigh\tRelErr\tTheoreticValue",file=datafile)

#Loop only once in the case of min # of person for a conflict
#In case of isProb = False we would not need the for loop, just one iteration
persons = number_persons if isProb else [0]
for p in persons: # for each number of days and persons
	if(isProb):
		print(f"Running with #persons {p}")
	out_run=run_simulator(p) # get the output results of a run
	print(*out_run,sep="\t",file=datafile) # write on a file
datafile.close() # close the file

import os
if(isProb): 
	os.system(f"python PlotResultsProb.py {number_days} {runs}")  
