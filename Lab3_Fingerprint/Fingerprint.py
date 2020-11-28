import hashlib
import math
import time #To remove
import sys

file = open('words_alpha.txt','r')

words = []
for f in file:
	words.append(f)
number_words = len(words)
print(f'Number of Words: {number_words}')

min_num_bits = 0
#max_num_bits = math.ceil(math.log(number_words,2))
max_num_bits = number_words//32
conflictHappened = True
end_loop = False
min_found = 999

print('\nSimulation')
###	BINARY SERACH	###
# while(end_loop is False):
# 	conflictHappened = False
# 	num_bits = min_num_bits + math.ceil((max_num_bits - min_num_bits)/2)
# 	print(max_num_bits,min_num_bits,num_bits)
# 	storage_length = 2**num_bits

# 	hash_words = set()
# 	for w in words:
# 		word_hash = hashlib.md5(w.encode('utf-8'))
# 		word_hash_int = int(word_hash.hexdigest(), 16)
# 		h = word_hash_int % storage_length

# 		if(h in hash_words):
# 			print(f'{num_bits} #bits are NOT enough')
# 			min_num_bits = num_bits
# 			conflictHappened = True
# 			break
# 		else:
# 			hash_words.add(h)

# 	if(conflictHappened is False):
# 		print(f'{num_bits} #bits are enough')
# 		max_num_bits = num_bits
# 		min_found = num_bits if num_bits<min_found else min_found

# 	if((max_num_bits - min_num_bits)<2):
# 		print('End loop: ', min_found)
# 		end_loop = True

# 	print()
# 	time.sleep(1)


if(True):
	conflict = True
	step = 33
	while(conflict is True):
		conflict = False
		num_bits = step
		storage_length = 2**num_bits

		hash_words = set()
		for w in words:
			word_hash = hashlib.md5(w.encode('utf-8'))
			word_hash_int = int(word_hash.hexdigest(), 16)
			h = word_hash_int % storage_length

			if(h in hash_words):
				print(f'{num_bits} #bits are NOT enough')
				conflict = True
				break
			else:
				hash_words.add(h)

		if(conflict==False):
			print('found: ',step)
		step+=1
print('End Simulation\n')

###	b^teo	###
#prob(conflic) = 1 - (1-1/number_words)**number_words
b_teo = math.log( number_words/0.5 ,2)
#b_teo = math.log (math.sqrt( 2*number_words*0.6931) , 2)
print(f'Theoretica number of bits reqired: {b_teo:.2f}')

###	Relation b^exp and b_teo	###
print(f'Ratio Simulated and Theoretical number of bits {(36/b_teo):.2f}')

### Memmory to store the hash table	###
size_hashtable = sys.getsizeof(hash_words)
print(f'Bytes required to store the hash words: {int(size_hashtable/1000)}kB')