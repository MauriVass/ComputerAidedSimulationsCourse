import hashlib
import math
import sys
from pympler import asizeof
import numpy as np
from scipy.stats import t

file = open('words_alpha.txt','r')
words_set = set()
mem = 0
for f in file:
	#Add word to the set without the ending '\n'
	words_set.add(f.strip())
number_words = len(words_set)
print(f'Number of Words: {number_words}')

debug = False

#Initial min value of bits
# b=math.log(number_words,2) gives a probability of false positive around 63%
min_num_bits = math.floor(math.log(number_words,2))
#Start searching from a bigger number than the min theoretical one
max_num_bits = math.ceil(math.log(number_words,2)) * 4
#This variable is used as loop exit condition: we found the minimum value of b^exp
end_loop = False
#This variable is used to store the minimum value of b^exp found and also
#to understand if this value can be found with the given value of max_num_bits (max_num_bits is not too small)
min_found = np.Inf
min_storage_length = -1
#Temporary variable
min_fingerprint_table = set()

print('\nSimulation')
print(f'Initial Values Bits. Min: {min_num_bits}, Max: {max_num_bits}')
###	BINARY SERACH	###
while(end_loop is False): #Loop until no conflict is found with the given b^exp value

	#This variable tells if for a specific value of b^exp a conflict happened(True) or not(False)
	conflictHappened = False

	#Start from the middle point between min and max
	num_bits = min_num_bits + math.ceil((max_num_bits - min_num_bits)/2.0)
	if(debug):
		print(f'Min: {min_num_bits}, #Bits: {num_bits}, Max: {max_num_bits}')
	storage_length = 2**num_bits

	#Use the 2 required data structures: fingerprint table and a python set
	#They are the same type what changes is how they are filled
	#Fingerprint table: only the word fingerprint
	#Python set: the word as it is
	fingerprint_table = set()
	#words_set = set()
	for w in words_set:
		#Add the word to the python set
		#words_set.add(w)

		#Calculate word Hash
		word_hash = hashlib.md5(w.encode('utf-8'))
		word_hash_int = int(word_hash.hexdigest(), 16)
		#Calculate element index [0,storage_length-1]
		h = word_hash_int % storage_length

		if(h in fingerprint_table): #Conflict
			print(f'{num_bits} bits are NOT enough')
			#A conflit is found this means that the number of bits must be increased
			min_num_bits = num_bits 
			conflictHappened = True
			break
		else:
			fingerprint_table.add(h) #The word is not present

	if(conflictHappened is False): #No Conflict
		print(f'{num_bits} bits are enough')
		#No conflit is found this means that the number of bits can be decreased
		#The search continues since a lower number may be found
		max_num_bits = num_bits
		#Store the minimum number of bits found so far
		if(num_bits<min_found):
			min_found = num_bits
			min_storage_length = storage_length
			min_fingerprint_table = fingerprint_table

	#Stop searching condition: no integer number between min and max
	if((max_num_bits - min_num_bits)/2<1):
		print('End loop. Min number bit found found: ', min_found)
		#Restore variables with the right value of bits
		num_bits = min_found
		storage_length = min_storage_length
		fingerprint_table = min_fingerprint_table
		#Remove references so that python may re-use that memory
		del min_fingerprint_table
		end_loop = True

#If the value of min_found did not change, it means the the initial max_num_bits value was too low. Exit
if(min_found==np.Inf):
	print('ERROR!! Starting point \'max_num_bits\' value was too low. Try increasing it!')
	exit(0)
print('End Simulation\n')

###	b^teo	###
#Solving the eq p(conflict) of Birthday Paradox in function of n(=2^b)
wanted_prob = 0.5
length_teo = -1.0*(number_words**2)/math.log(1.0-wanted_prob)/2.0
b_teo = math.log( length_teo ,2)
print(f'Theoretica number of bits reqired: {b_teo:.2f}')

###	Relation b^exp and b_teo	###
b_teo_ceil = math.ceil(b_teo)
print(f'Ratio Simulated and Theoretical number of bits: {num_bits}/{b_teo_ceil}={(num_bits/b_teo_ceil):.2f}')

###	Min theoretical required memories ###
#The average english words length is 4.79 characters (1 char = 8 bits)
#Formula: total_size_Byte = number_words * bits_for_word / 8 bits
theoretical_size_fpt = number_words * num_bits / 8.0
theoretical_size_word_set = number_words * 4.79 # equivalent to ~38.32 bits

### Memory to store the fp table and the set	###
#asizeof returns the size in Bytes
size_hashtable = asizeof.asizeof(fingerprint_table)
size_word_set = asizeof.asizeof(words_set)
print('Memory required:')
print(f'\tTo store the fingerprint table: {(size_hashtable/(1024**2)):.2f} MB, for the python set: {(size_word_set/(1024**2)):.2f} MB')
print(f'\tTheoretical memory fingerprint table: {(theoretical_size_fpt/(1024**2)):.2f} MB, theoretical memory python set: {(theoretical_size_word_set/(1024**2)):.2f} MB')

###	prob False Positive	###

#Returns the (fake) hash of a word
#This fucntion is used to check the probability of false positive
def generateWord(max_val):
	return int(np.random.uniform(high=max_val))
def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) # std dev
	ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave if ave>0 else 0
	return ave, ci, rel_err

initial_seed = 2500
confidence_level = 0.95
n_runs = 3
number_words_checkcollision = 5 * 10**6
print("\nInitial seed: ",initial_seed)
print("Confidence level: ",confidence_level)
print("Number of runs: ",n_runs)
print("Number words used for checking collisions: ",number_words_checkcollision)

#Store the value of probability of false positive for each run
prob_collision_fp = np.zeros(n_runs)
prob_collision_set = np.zeros(n_runs)

for r in range(n_runs):
	num_collision_fp = 0
	num_collision_set = 0
	for i in range(number_words_checkcollision):
		#Generate 'fake' word hash(es). Fake because they are just ~rnd number between [0,n)
		word_hash = generateWord(storage_length)
		#Check if the word is present but it should not
		isPresent_fp = word_hash in fingerprint_table
		isPresent_set = word_hash in words_set

		#If present is True it means the the fake word is present
		if(isPresent_fp):
			num_collision_fp+=1
		if(isPresent_set):
			num_collision_set+=1
	prob_collision_fp[r] = num_collision_fp/number_words_checkcollision
	prob_collision_set[r] = num_collision_set/number_words_checkcollision
# print(prob_collision_fp) #The result is something like this: [4.e-07 4.e-07 0]
# print(prob_collision_set) #[0. 0. 0.]

ave_fp, ci_fp, rel_err_fp = evaluate_conf_interval(prob_collision_fp)
ave_set, ci_set, rel_err_set = evaluate_conf_interval(prob_collision_set)
print(f'Fingerprint Set: prob: {ave_fp}, CI: {ci_fp}, Reletive Err: {rel_err_fp}')
print(f'Python Set: prob: {ave_set}, CI: {ci_set}, Reletive Err: {rel_err_set}')

#This should be simulated but the number of bits is so high that it is ok to calculate theoretically
prob_false_pos = number_words / storage_length
print(f'Probability False Positive: {prob_false_pos}')
