import hashlib
import math
import numpy as np
from pympler import asizeof
from scipy.stats import t
import sys 

def generateWord(max_val):
	return int(np.random.uniform(high=max_val))

def compute_all_hashes(md5, num_hashes, b):
	# returns the list of num_hashes indexes corresponding to all the bits to update in a bloom filter
	# md5 is the hash integer value obtained by md5, on 128 bits
	# num_hashes is the number of hash values to generate
	# b is the number of bits such that the bit array is of size 2**b
	debug=False # flag to obtain debug info, useful to understand how the function work
	bits_to_update=[] # the list of bits to update is initially empty
	if (b+3*num_hashes>128): # check the condition about the max number of supported hashes
		print("Error - at most 32 hashes")
		return -1
	for i in range(num_hashes): # for each hash to generate
		if debug:
			print("{0:b}".format(md5)) # print the md5 value in binary
		value=md5 % (2 ** b) # take the last b bits for the hash value
		bits_to_update.append(value) # add the hash value in the list
		if debug:
			print("Hash value:",value,"\t{0:b}".format(value)) # debug
		md5 = md5 // (2 ** 3) # right-shift the md5 by 3 bits
	return bits_to_update

# compute the hash
# word_hash = hashlib.md5('ciao'.encode('utf-8')) # example for ’ciao’
# word_hash_int = int(word_hash.hexdigest(), 16) # compute the hash
# all_bits_to_update=compute_all_hashes(word_hash_int, 32, 24) # compute 32 hash values on 24 bits
# print(all_bits_to_update) # show the obtained hash values

# exit(0)

def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) # std dev
	ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width
	# ave = x # average. This is the total number of collision divided by the total number of persons
	# stddev = np.sqrt(x*(1-x)) # std dev
	# ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave if ave>0 else 0
	return ave, ci, rel_err

def run_simulator(num_bits):
	np.random.seed(initial_seed)
	print(f'Num bits: {num_bits}')
	storage_length = 2**num_bits
	bit_string_array = np.zeros(storage_length, dtype=np.int8)

	#Use a different number of hashes depensing if it is a BitString Array (1 hash)
	#Or it is a Bloom filter application (k hashes)
	if(bloom_filter==0):
		num_hashes = 1
	else:
		#Theoretical formula to calculate the number of hashes needed
		#You should check both upper and lower integer( ceil() and floor() ) and pick the best one
		#But usually truncate to the near integer works fine
		num_hashes = int((storage_length/number_words)*math.log(2))
		num_hashes = num_hashes if num_hashes > 0 else 1

	for w in words:
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		#h = word_hash_int % storage_length
		hashes = compute_all_hashes(word_hash_int,num_hashes,num_bits)
		#print(hashes)
		for h in hashes:
			if(bit_string_array[h]==1): #Conflict
				#num_collision+=1
				_=0
			else:
				bit_string_array[h]=1
	
	prob_collision = np.zeros(n_runs)
	for r in range(n_runs):
		num_collision = 0
		for i in range(number_words_checkcollision):
			#Generate 'fake' word hash(es). Fake because they are just rnd number between [0,n)
			word_indexes = [generateWord(storage_length) for _ in range(num_hashes)]
			#print(word_indexes)
			isPresent = True
			#Loop over all fake word hashes to check if the word is present but shouldn't
			#All bit_string_array[word_index] should be 1 for a collision -> 
			#if just one is 0 it means that the fake word is not present
			for word_index in word_indexes:
				if(bit_string_array[word_index]==0): #Conflict
					isPresent=False
					break
			#If present is True it means the the fake word is present
			if(isPresent):
				num_collision+=1
		prob = num_collision/number_words_checkcollision
		prob_collision[r] = prob

	#pr(FP)=pr(for each k, bs_arr[k]=1)=(# 1s/# length)^k
	theoretical_probability = (np.sum(bit_string_array)/storage_length)**num_hashes
	ave, ci, rel_err = evaluate_conf_interval(prob_collision)
	memory_occupacy = (asizeof.asizeof(bit_string_array))/1024**2
	theoretical_mem_occ = ((number_words * num_bits)/8)/1024**2
	if(bloom_filter==0):
		return num_bits, ave - ci, ave, ave + ci, rel_err, theoretical_probability, memory_occupacy, theoretical_mem_occ
	else:
		return num_bits, num_hashes, ave - ci, ave, ave + ci, rel_err, theoretical_probability, memory_occupacy, theoretical_mem_occ
	
	# prob_false_pos = number_words / storage_length
	# size_bitarray = asizeof.asizeof(bit_string_array)
	# theoretical_size = (number_words * num_bits) / 8
	# #prob_bloom_fil = (1-math.exp(-number_words*storage_length/))
	# return num_bits, prob_false_pos, size_bitarray, theoretical_size

#Store english vocabulary
file = open('words_alpha.txt','r')
words = []
for f in file:
	words.append(f)
number_words = len(words)
print(f'Number of Words: {number_words}')

initial_seed = 2500
confidence_level = 0.95
n_runs = 4
bloom_filter = int(sys.argv[1])
number_words_checkcollision = 1000

datafile = open(f"bit_string_array{bloom_filter}.dat", "w")
if(bloom_filter==0):
	print("nbits\tciLow\tave\tciHigh\trel_err\tthProb\tmemOccup\tth_memOccup",file=datafile)
else:
	print("nbits\tnHashes\tciLow\tave\tciHigh\trel_err\tthProb\tmemOccup\tth_memOccup",file=datafile)
#print("num_bits, ave - ci, ave, ave + ci, rel_err, theoretical_occupacy")
# print("nbits\tprob_FalsePos\tsize\ttheoretical_size",file=datafile)

possible_num_bits = [19, 20, 21, 22, 23, 24]
for num_bits in possible_num_bits:
	out_run=run_simulator(num_bits) # get the output results of a run
	print(*out_run,sep="\t", file=datafile) # write on a file
	#print(*out_run,sep="\t")
datafile.close() # close the file

import os
os.system(f'python PlotResultsBSA.py {bloom_filter}')





		