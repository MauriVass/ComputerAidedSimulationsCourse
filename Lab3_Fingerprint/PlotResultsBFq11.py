import hashlib
import math
import numpy as np
import matplotlib.pyplot as plt
from bitarray import bitarray
import os

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

def run_simulator(num_bits):
	print(f'Num bits: {num_bits}')
	storage_length = 2**num_bits

	bit_string_array = storage_length * bitarray('0')

	#Theoretical formula to calculate the number of hashes needed
	#You should check both upper and lower integer( ceil() and floor() ) and pick the best one
	#But usually truncate to the near integer works fine
	num_hashes = round((storage_length/number_words)*math.log(2))
	num_hashes = num_hashes if num_hashes > 0 else 1

	#x values: num of words added
	x = []
	#y values: the actuall number of distinct words
	y = []
	y_th = []
	rel_errs = []
	distinct_words=0
	for i,w in enumerate(words):
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		hashes = compute_all_hashes(word_hash_int,num_hashes,num_bits)

		already_present = True
		for h in hashes:
			if(bit_string_array[h]==False):
				bit_string_array[h]=True
				already_present = False

		if (already_present==False):
			distinct_words+=1

		#Store some value for the plot every frequency steps
		if(i%frequency==0 and i>start):
			bits_equal1 = np.sum(bit_string_array.tolist())
			th_value = - (storage_length/num_hashes)*math.log(1-bits_equal1/storage_length)
			# |simulated-real|/real
			rel_err = np.abs(i-th_value)/th_value

			x.append(i)
			y.append(distinct_words)
			y_th.append(th_value)
			rel_errs.append(rel_err)
	return x, y, y_th, rel_errs

#Store english vocabulary
file = open('words_alpha.txt','r')
words = set()
for f in file:
	words.add(f)
number_words = len(words)
print(f'Number of Words: {number_words}')

frequency=35000
start = 5000

possible_num_bits = range(19,24)
print(f'Possible number of bits: {possible_num_bits}')
plt.figure(figsize=(12, 6), dpi=80)
colors = [(1,0,0),(0,1,0),(0,0,1),(1,0.5,0),(1,0,1),(0,1,1)]
for num_bits in possible_num_bits:
	x,y,y_th,rel_errs=run_simulator(num_bits) # get the output results of a run

	plt.plot(x,rel_errs, marker="o", label=f'#Bits: {num_bits}')

title = f'Comparison Theory vs Simulation number distinct Words'
plt.title(title)

plt.legend(loc='best')
plt.xlabel('Number distinct Words added')
plt.ylabel('Relative Errors')

t = title.replace(' ','')
save_title = (f'Images/{t}q11')
plt.savefig(save_title)

plt.show()