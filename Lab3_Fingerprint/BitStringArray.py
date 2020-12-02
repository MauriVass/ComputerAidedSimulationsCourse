import hashlib
import math
import numpy as np

file = open('words_alpha.txt','r')

words = []
for f in file:
	words.append(f)
number_words = len(words)
print(f'Number of Words: {number_words}')

datafile = open(f"bit_string_array.dat", "w")
print("nbits\tprob",file=datafile)

print('Start Simulation\n')
possible_num_bits = [19]#, 20, 21, 22, 23, 24]
for num_bits in possible_num_bits:
	print(f'Num bits: {num_bits}')
	num_collision = 0
	storage_length = 2**num_bits
	bit_string_array = np.zeros(storage_length)

	for w in words:
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		h = word_hash_int % storage_length

		if(bit_string_array[h]==1): #Conflict
			num_collision+=1
		else:
			bit_string_array[h]=1

	theoretical_mem = 
	size_bitarray = asizeof.asizeof(bit_string_array)
	output = f'{num_bits}\t{num_collision/number_words}\t{size_bitarray}'


print('End Simulation\n')

for k,v in prob_collision.items():
	print(f'#Bits: {k}, Prob of conflicts: {v:.4f}')
	print(f'{k}\t{v[0]}',file=datafile)
