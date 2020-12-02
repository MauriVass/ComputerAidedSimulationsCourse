import hashlib
import math
import time #To remove
import sys
from pympler import asizeof

file = open('words_alpha.txt','r')

words = []
for f in file:
	words.append(f)
number_words = len(words)
print(f'Number of Words: {number_words} {math.log(number_words)}')

debug = False

min_num_bits = 0
#Start searching from a bigger number than the theoretical one
max_num_bits = math.ceil(math.log(number_words,2)) * 5
conflictHappened = True
end_loop = False
min_found = 999

print('\nSimulation')
###	BINARY SERACH	###
while(end_loop is False): #Loop until any conflict is found
	conflictHappened = False
	#Start from the middle point between min and max
	num_bits = min_num_bits + math.ceil((max_num_bits - min_num_bits)/2)
	if(debug):
		print(f'Min: {min_num_bits}, Max: {max_num_bits}, #Bits: {num_bits}')
	storage_length = 2**num_bits

	hash_words = set()
	for w in words:
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		h = word_hash_int % storage_length

		if(h in hash_words): #Conflict
			print(f'{num_bits} #bits are NOT enough')
			#A conflit is found this means that the number of bits must be increased
			min_num_bits = num_bits 
			conflictHappened = True
			break
		else:
			hash_words.add(h)

	if(conflictHappened is False): #No Conflict
		print(f'{num_bits} #bits are enough')
		#No conflit is found this means that the number of bits must be decreased, since a lower number may be found
		max_num_bits = num_bits
		#Store the minimum number of bits found so far
		min_found = num_bits if num_bits<min_found else min_found
	#Stop searching condition: no integer number between min and max
	if((max_num_bits - min_num_bits)/2<1):
		print('End loop: ', min_found)
		end_loop = True
#If the value of min_found does not change, it means the the initial max point was too low. Exit
if(min_found==999):
	print('ERROR!! Starting point: max_num_bits has a too low value. Try increase it!')
	exit(0)

###	Normal SERACH	###
# conflict = True
# step = 0
# while(conflict is True): #Loop until any conflict is found
# 	conflict = False
# 	num_bits = step
# 	storage_length = 2**num_bits

# 	hash_words = set()
# 	for w in words:
# 		#Calculate Hash
# 		word_hash = hashlib.md5(w.encode('utf-8'))
# 		word_hash_int = int(word_hash.hexdigest(), 16)
# 		#Calculate element index [0,storage_length-1]
# 		h = word_hash_int % storage_length

# 		if(h in hash_words):  #Conflict
# 			print(f'{num_bits} #bits are NOT enough')
# 			conflict = True
# 			break
# 		else:
# 			hash_words.add(h)
# 	#Any conflict found. Exit loop
# 	if(conflict==False):
# 		print('found: ',step)
# 		min_num_bits = step
# 	step+=1
print('End Simulation\n')

###	b^teo	###
#prob(conflic) = 1 - (1-1/number_words)**number_words
#b_teo = math.log( number_words/0.5 ,2)
b_teo = math.log( math.sqrt( 2*number_words* math.log(1.0/(1-0.5),2) ) , 2 )
print(f'Theoretica number of bits reqired: {b_teo:.2f}')

###	Relation b^exp and b_teo	###
print(f'Ratio Simulated and Theoretical number of bits {(min_num_bits/b_teo):.2f}')

### Memmory to store the hash table	###
size_array = asizeof.asizeof(words)
size_hashtable = asizeof.asizeof(hash_words)
print(f'Memory required to store the hash table: {int(size_hashtable/1000)}kB, the array: {int(size_array/1000)}kB')