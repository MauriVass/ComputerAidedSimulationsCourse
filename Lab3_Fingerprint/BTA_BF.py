import hashlib
import math
import numpy as np
from pympler import asizeof
from scipy.stats import t
from bitarray import bitarray

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--runs', type=int, help='Number or runs: (r>1)', required=False, default=2)
parser.add_argument('--dataS', type=int, choices=[0,1], help='Data Structure to be used: 0:bit string array, 1:simple bloom filter', required=False, default=0)
parser.add_argument('--words', type=int, help='Number words used for checking collisions', required=False, default=30000)
args = parser.parse_args()

initial_seed = 2500
np.random.seed(initial_seed)
confidence_level = 0.95
n_runs = args.runs
#This can be [0,1]: 0:bit string array, 1:simple bloom filter
data_struc_type = args.dataS

if(data_struc_type==0):
	print('Data Structure: Bit String Array')
else:
	print('Data Structure: Bloom Filter')
	number_words_checkcollision = args.words
print("Initial seed: ",initial_seed)
print("Confidence level: ",confidence_level)
if(data_struc_type==1):
	print("Number of runs: ",n_runs)
	print("Number words used for checking collisions: ",number_words_checkcollision)

#Returns the (fake) hash of a word
#This fucntion is used to check the probability of false positive
def generateWord(max_val):
	return int(np.random.uniform(high=max_val))

def compute_all_hashes(md5, num_hashes, b):
	# returns the list of num_hashes indexes corresponding to all the bits to update in a bloom filter
	# md5 is the hash integer value obtained by md5, on 128 bits
	# num_hashes is the number of hash values to generate
	# b is the number of bits such that the bit array is of size 2**b
	debug=False # flag to obtain debug info, useful to understand how the function work
	bits_to_update=[] # the list of bits to update is initially empty

	#This calculates the shift based on the number of hashes needed and the number of bits used
	#This allows 'more' independencies between the
	shift = int((128-b)/num_hashes)
	shift = 3 #shift if shift<b else b
	if debug:
		print(f'Number Hashes: {num_hashes}, number Bits: {b}, Shift value: {shift}')
	if (b+shift*num_hashes>128): # check the condition about the max number of supported hashes
		print(f"Error - at most {int((128-b)/shift)} hashes")
		return -1
	for i in range(num_hashes): # for each hash to generate
		if debug:
			print("{0:b}".format(md5)) # print the md5 value in binary
		value=md5 % (2 ** b) # take the last b bits for the hash value
		bits_to_update.append(value) # add the hash value in the list
		if debug:
			print("Hash value:",value,"\t{0:b}".format(value)) # debug
		md5 = md5 // (2 ** shift) # right-shift the md5 by 'shift' bits
	return bits_to_update

def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) # std dev
	ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave if ave>0 else -1
	return ave, ci, rel_err

def run_simulator(num_bits):
	print(f'Num bits: {num_bits}')
	#Calculate the length of the structure 2^nbits
	storage_length = 2**num_bits

	#Bit String Array/Bloom filter application
	bit_string_array = storage_length * bitarray('0')

	#Comparison: bitarray('0') vs [False]
	#The implementation with bitarray() takes much less storage memory
	# print((asizeof.asizeof(bit_string_array))/1024**2) 
	# print( (asizeof.asizeof(storage_length * [False]))/1024**2)

	#Use a different number of hashes depending if it is a BitString Array (1 hash)
	#Or it is a Bloom filter application (k hashes)
	if(data_struc_type==0):
		num_hashes = 1
	else:
		#Theoretical formula to calculate the number of hashes needed
		#You should check both upper and lower integer( ceil() and floor() ) and pick the best one
		#But usually round to the near integer works fine
		num_hashes = round((storage_length/number_words)*math.log(2))
		num_hashes = num_hashes if num_hashes > 0 else 1

	for w in words: #for each word
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		hashes = compute_all_hashes(word_hash_int,num_hashes,num_bits)

		for h in hashes: #loop over all hash(es)
			if(bit_string_array[h]==False):
				bit_string_array[h]=True

	#Calcualte the probability of false positive:
	#Analitically for Bit String Array,
	#By simulation for Bloom Filters
	if(data_struc_type==0):		
		#pr(FP)=pr(for each k, bs_arr[k]=1)=(# 1s/# length)^k
		prob_fp = np.sum( bit_string_array.tolist() )/storage_length
	else:
		prob_collision = np.zeros(n_runs)
		for r in range(n_runs):
			num_collision = 0
			for i in range(number_words_checkcollision):
				#Generate 'fake' word hash(es). Fake because they are just rnd number between [0,n)
				word_indexes = [generateWord(storage_length) for _ in range(num_hashes)]
				isPresent = True
				#Loop over all fake word hashes to check if the word is present but shouldn't
				#All bit_string_array[word_index] should be 1 for a collision -> 
				#if just one is 0 it means that the fake word is not present (exit the loop)
				for word_index in word_indexes:
					if(bit_string_array[word_index]==False):
						isPresent=False
						break

				#If present is True it means the the fake word is present
				if(isPresent):
					num_collision+=1
			prob = num_collision/number_words_checkcollision
			prob_collision[r] = prob

		# print(prob_collision) #Very close probabilities. This explains why few n_runs and few number_words_checkcollision are enough
		ave, ci, rel_err = evaluate_conf_interval(prob_collision)

	#number_words * 1: 1 is the number of bits used for boolean storage [True, False] (does not depend on the num_bits)
	theoretical_mem_occ = ((number_words * 1)/8.0)/1024**2

	memory_occupacy = (asizeof.asizeof(bit_string_array))/1024**2
	if(data_struc_type==0):
		return num_bits, prob_fp, memory_occupacy, theoretical_mem_occ
	else:
		theoretical_prob_fp = (1-math.exp(-num_hashes*number_words/storage_length))**num_hashes
		return num_bits, num_hashes, ave - ci, ave, ave + ci, rel_err, theoretical_prob_fp, memory_occupacy, theoretical_mem_occ

#Store english vocabulary
file = open('words_alpha.txt','r')
words = set()
for f in file:
	words.add(f)
number_words = len(words)
print(f'Number of Words: {number_words}')

if(data_struc_type==0):
	datafile = open(f"bit_string_array_results.dat", "w")
	print("nbits\tprobFP\tmemOccup\tth_memOccup",file=datafile)
else:
	datafile = open(f"bloom_filters_results.dat", "w")
	print("nbits\tnHashes\tciLow\tave\tciHigh\trel_err\tthProbFP\tmemOccup\tth_memOccup",file=datafile)

possible_num_bits = [19, 20, 21, 22, 23, 24]
print(f'Possible number of bits: {possible_num_bits}\n')
print('Simulation:')
for num_bits in possible_num_bits:
	out_run=run_simulator(num_bits) # get the output results of a run
	print(*out_run,sep="\t", file=datafile) # write on a file
	#print(*out_run,sep="\t")
print('End Simulation')
datafile.close() # close the file

import os
os.system(f'python PlotResults.py {data_struc_type}')
