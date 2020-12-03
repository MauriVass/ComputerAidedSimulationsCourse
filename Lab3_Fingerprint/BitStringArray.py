import hashlib
import math
import numpy as np
from pympler import asizeof
from scipy.stats import t

def generateWord(max_val):
	return int(np.random.uniform(high=max_val))

def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) # std dev
	ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width
	# ave = x # average. This is the total number of collision divided by the total number of persons
	# stddev = np.sqrt(x*(1-x)) # std dev
	# ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave # if ave>0 else # relative error
	return ave, ci, rel_err

def run_simulator(num_bits):
	np.random.seed(initial_seed)
	print(f'Num bits: {num_bits}')
	storage_length = 2**num_bits
	bit_string_array = np.zeros(storage_length)

	for w in words:
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		h = word_hash_int % storage_length

		if(bit_string_array[h]==1): #Conflict
			#num_collision+=1
			_=0
		else:
			bit_string_array[h]=1

	prob_collision = np.zeros(n_runs)
	for r in range(n_runs):
		num_collision = 0
		number_words_checkcollision = 10000
		for i in range(number_words_checkcollision):
			word_index = generateWord(storage_length)
			if(bit_string_array[word_index]==1): #Conflict
				num_collision+=1
			else:
				bit_string_array[h]=1

		prob = num_collision/number_words_checkcollision
		prob_collision[r] = prob
	theoretical_occupacy = number_words/storage_length
	ave, ci, rel_err = evaluate_conf_interval(prob_collision)
	return num_bits, ave - ci, ave, ave + ci, rel_err, theoretical_occupacy

#Store english vocabulary
file = open('words_alpha.txt','r')
words = []
for f in file:
	words.append(f)
number_words = len(words)
print(f'Number of Words: {number_words}')

initial_seed = 2500
confidence_level = 0.95
n_runs = 3

datafile = open(f"bit_string_array.dat", "w")
print("nbits\tciLow\tave\tciHigh\trel_err\ttheoretical",file=datafile)
#print("num_bits, ave - ci, ave, ave + ci, rel_err, theoretical_occupacy")

possible_num_bits = [19, 20, 21, 22, 23, 24]
for num_bits in possible_num_bits:
	out_run=run_simulator(num_bits) # get the output results of a run
	print(*out_run,sep="\t", file=datafile) # write on a file

	#print(*out_run,sep="\t")
datafile.close() # close the file

#size_bitarray = asizeof.asizeof(bit_string_array)

import os
os.system('python PlotResults.py')





		