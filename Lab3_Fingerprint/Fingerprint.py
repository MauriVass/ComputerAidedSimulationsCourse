import hashlib
import math
import sys
from pympler import asizeof
import numpy as np
from scipy.stats import t

file = open('words_alpha.txt','r')

words_list = []
for f in file:
	words_list.append(f)
number_words = len(words_list)
print(f'Number of Words: {number_words} {math.log(number_words,2)}')

debug = False

min_num_bits = 0
#Start searching from a bigger number than the theoretical one
max_num_bits = math.ceil(math.log(number_words,2)) * 2
conflictHappened = True
end_loop = False
min_found = 999

print('\nSimulation')
###	BINARY SERACH	###
while(end_loop is False): #Loop until no conflict is found
	conflictHappened = False
	#Start from the middle point between min and max
	num_bits = min_num_bits + math.ceil((max_num_bits - min_num_bits)/2)
	if(debug):
		print(f'Min: {min_num_bits}, Max: {max_num_bits}, #Bits: {num_bits}')
	storage_length = 2**num_bits

	fingerprint_table = set()
	for w in words_list:
		#Calculate Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		h = word_hash_int % storage_length

		if(h in fingerprint_table): #Conflict
			print(f'{num_bits} #bits are NOT enough')
			#A conflit is found this means that the number of bits must be increased
			min_num_bits = num_bits 
			conflictHappened = True
			break
		else:
			fingerprint_table.add(h)

	if(conflictHappened is False): #No Conflict
		print(f'{num_bits} #bits are enough')
		#No conflit is found this means that the number of bits must be decreased
		#The search continues since a lower number may be found
		max_num_bits = num_bits
		#Store the minimum number of bits found so far
		min_found = num_bits if num_bits<min_found else min_found
	#Stop searching condition: no integer number between min and max
	if((max_num_bits - min_num_bits)/2<1):
		print('End loop: ', min_found)
		num_bits = min_found
		end_loop = True
#If the value of min_found does not change, it means the the initial max point was too low. Exit
if(min_found==999):
	print('ERROR!! Starting point \'max_num_bits\' value was too low. Try increasing it!')
	exit(0)
print(f'Found: {num_bits}')
###	Normal SERACH	###
# conflict = True
# step = 0
# while(conflict is True): #Loop until any conflict is found
# 	conflict = False
# 	num_bits = step
# 	storage_length = 2**num_bits

# 	#hash_words = set()
# 	hash_words = np.zeros(storage_length)
# 	for w in words:
# 		#Calculate Hash
# 		word_hash = hashlib.md5(w.encode('utf-8'))
# 		word_hash_int = int(word_hash.hexdigest(), 16)
# 		#Calculate element index [0,storage_length-1]
# 		h = word_hash_int % storage_length

# 		# if(h in hash_words):  #Conflict
# 		# 	print(f'{num_bits} #bits are NOT enough')
# 		# 	conflict = True
# 		# 	break
# 		# else:
# 		# 	hash_words.add(h)
# 		if(hash_words[h]==0): #Conflict
# 			print(f'{num_bits} #bits are NOT enough')
# 			#A conflit is found this means that the number of bits must be increased
# 			min_num_bits = num_bits 
# 			conflict = True
# 			break
# 		else:
# 			hash_words[h] = 1
# 	#Any conflict found. Exit loop
# 	if(conflict==False):
# 		print('found: ',step)
# 		min_num_bits = step
# 	step+=1
print('End Simulation\n')

###	b^teo	###
#https://stackoverflow.com/questions/62664761/probability-of-hash-collision
b_teo = math.log( (2*storage_length*math.log(1/(1-0.5))) ,2)
#b_teo = math.ceil(b_teo)
print(f'Theoretica number of bits reqired: {b_teo:.2f}')

###	Relation b^exp and b_teo	###
print(f'Ratio Simulated and Theoretical number of bits: {num_bits}/{b_teo:.2f}={(num_bits/b_teo):.2f}')

###	Min theoretical required memory ###
#The average english words length is 4.7 characters
#total_size_Byte = number_words * bits_for_word / 8 bits
theoretical_size = (number_words * num_bits)/8

### Memory to store the hash table	###
#asizeof returns the size in Bytes
size_list = asizeof.asizeof(words_list)
size_hashtable = asizeof.asizeof(fingerprint_table)
print(f'Memory required to store the fingerprint table: {(size_hashtable/(1024**2)):.3f} MB, the list: {(size_list/(1024**2)):.3f} MB, theoretical memory: {(theoretical_size/(1024**2)):.3f} MB')


###	prob False Positive	###
prob_false_pos = number_words / storage_length
print(f'Probability False Positive: {prob_false_pos}')

'''
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
	rel_err = ci / ave if ave>0.001 else -1
	return ave, ci, rel_err

def run_simulator(num_bits):
	np.random.seed(initial_seed)
	print(f'Num bits: {num_bits}')
	storage_length = 2**num_bits

	prob_collision = np.zeros(n_runs)
	for r in range(n_runs):
		num_collision = 0
		number_words_checkcollision = 10000
		for i in range(number_words_checkcollision):
			word_index = generateWord(storage_length)
			if(word_index in hash_words): #Conflict
				num_collision+=1

		prob = num_collision/number_words_checkcollision
		prob_collision[r] = prob
	print(prob_collision)
	theoretical_occupacy = number_words/storage_length
	ave, ci, rel_err = evaluate_conf_interval(prob_collision)
	return num_bits, ave - ci, ave, ave + ci, rel_err, theoretical_occupacy

confidence_level = 0.95
initial_seed = 1234
#n_runs = 5
#outp = run_simulator(num_bits)
#print(outp)
'''