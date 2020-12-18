import hashlib
import math
import numpy as np
import matplotlib.pyplot as plt
from pympler import asizeof
from scipy.stats import t
from bitarray import bitarray
import sys 
import os

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

def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) # std dev
	ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave if ave>0 else 0
	return ave, ci, rel_err

def run_simulator(num_bits):
	np.random.seed(initial_seed)
	print(f'Num bits: {num_bits}')
	storage_length = 2**num_bits

	if(data_struc_type==2):
		bit_string_array = np.zeros(storage_length, dtype=np.int8)
	else:
		bit_string_array = storage_length * bitarray('0')

	#Use a different number of hashes depensing if it is a BitString Array (1 hash)
	#Or it is a Bloom filter application (k hashes)
	if(data_struc_type==0):
		num_hashes = 1
	else:
		#Theoretical formula to calculate the number of hashes needed
		#You should check both upper and lower integer( ceil() and floor() ) and pick the best one
		#But usually truncate to the near integer works fine
		num_hashes = int((storage_length/number_words)*math.log(2))
		num_hashes = num_hashes if num_hashes > 0 else 1

	x = []
	y = []
	y_th = []
	distinct_words=0
	for i,w in enumerate(words):
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		#h = word_hash_int % storage_length
		hashes = compute_all_hashes(word_hash_int,num_hashes,num_bits)
		#print(hashes)
		already_present = True
		for h in hashes:
			if(bit_string_array[h]==False):
				bit_string_array[h]=True
				already_present = False

		if (already_present==False):
			distinct_words+=1
		if(i%frequency==0 and i>start):
			bits_equal1=np.sum(bit_string_array.tolist())
			th_value = - (storage_length/num_hashes)*math.log(1-bits_equal1/storage_length)
			x.append(i)
			y.append(distinct_words)
			y_th.append(th_value)
	return x, y, y_th
# prob_false_pos = number_words / storage_length
# size_bitarray = asizeof.asizeof(bit_string_array)
# theoretical_size = (number_words * num_bits) / 8
# #prob_bloom_fil = (1-math.exp(-number_words*storage_length/))
# return num_bits, prob_false_pos, size_bitarray, theoretical_size

#Store english vocabulary

#if(os.path.exists('Temp')==False):
#  !git clone https://github.com/MauriVass/Temp.git
file = open('words_alpha.txt','r')
words = []
for f in file:
	words.append(f)
number_words = len(words)
print(f'Number of Words: {number_words}')

initial_seed = 2500
confidence_level = 0.95
#This can be [0,1,2]: 0:bit string array, 1:simple bloom filter, 2:counting bloom filter
data_struc_type = int(sys.argv[1])
frequency=40000
start = 70000
	# datafile = open(f"bit_string_array{data_struc_type}.dat", "w")
	# if(data_struc_type==0):
	# 	print("nbits\tciLow\tave\tciHigh\trel_err\tthProb\tmemOccup\tth_memOccup",file=datafile)
	# else:
	# 	print("nbits\tnHashes\tciLow\tave\tciHigh\trel_err\tthProb\tmemOccup\tth_memOccup",file=datafile)
#print("num_bits, ave - ci, ave, ave + ci, rel_err, theoretical_occupacy")
# print("nbits\tprob_FalsePos\tsize\ttheoretical_size",file=datafile)

possible_num_bits = range(19,24)
plt.figure(figsize=(12, 6), dpi=80)
for num_bits in possible_num_bits:
	x,y,y_th=run_simulator(num_bits) # get the output results of a run
	#print(*out_run,sep="\t", file=datafile) # write on a file
	#print(*out_run,sep="\t")
	#print(x,y,y_th)
	plt.plot(x,y_th, marker="x")
	#Simulation
	plt.plot(x,y, marker="o", label=num_bits)

plt.plot([],[], marker="x", label='Theoretical')
plt.plot(x,x, c='blue' label='Stright line (m=1)')
title = f'Optional11'
plt.title(title)

plt.legend(loc='upper left')
# plt.xscale("log")
# plt.yscale("log")
plt.xlabel('Number of Words added')
plt.ylabel('Number of distinct Words')

save_title = (f'Images/{title}top')
plt.savefig(save_title)

plt.show()