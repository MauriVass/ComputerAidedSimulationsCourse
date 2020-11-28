import numpy as np
import random
from scipy.stats import t
import sys

# initial settings
initial_seed = 2502
confidence_level = 0.95
n_bins = int(sys.argv[1]) #can be 1,2,4
runs = int(sys.argv[2]) # number of runs
debug=False

# create list of inputs
input_list=[]
for i in (2,3,4,5):
    a=[x*10**i for x in (1,2,4,8)]
    input_list.extend(a)
input_list.extend([1000000])
input_list = np.array(input_list)

# print input parameters
print("*** INITIAL SETTINGS ***")
print("Bins/Balls number for the simulation:")
print(input_list)
print("Initial seed",initial_seed)
print("Confidence level",confidence_level)
print("Number of runs",runs)
print("*** END INITIAL SETTINGS ***")

# function to compute confidence intervals
def evaluate_conf_interval(x):
    # x is list of all the experimental rules, one for each run
    t_sh = t.ppf((confidence_level + 1) / 2, df=runs - 1) # threshold for t_student
    ave = x.mean() # average
    stddev = x.std(ddof=1) # std dev
    ci = t_sh * stddev / np.sqrt(runs) # confidence interval half width
    rel_err = ci / ave # relative error
    if debug:
        print("Min", x.min(), "Ave", ave, "Max", x.max())
    return ave, ci, rel_err

def run_simulator(n): # run the bins-and-ball model for n bins and for multiple runs
    random.seed(a=initial_seed) # reset initial seed
    maxvec = np.full(runs, 0) # init vector for the maximum for each run
    for r in range(runs): # for each run
        bins = np.full(n, 0) # bins[i] is the occupancy of bin i; start from empty bins
        for i in range(n): # for each ball
            rnd_bins = random.sample(range(0, n), n_bins)
            ind = -1
            min_val = 999
            for i in rnd_bins:
                if(min_val > bins[i]):
                    min_val = bins[i]
                    ind = i
            bins[ind] = bins[ind] + 1 # drop ball randomly and update bins
        maxvec[r] = bins.max() # compute the max occupancy
    ave, ci, rel_err = evaluate_conf_interval(maxvec) # evaluate the confidence intervals
    lower_bound = np.log(n) / np.log(np.log(n)) # theoretical formula
    return n, lower_bound, 3 * lower_bound, ave - ci, ave, ave + ci, rel_err

#########################
# main simulation engine
#########################
# open the outfile file and write the header

#for i in [3,5,10,20]:
 #   runs = i
datafile = open(f"binsballs{n_bins}_runs{runs}.dat", "w")
print("n\tLowerbound\t3*Lowerbound\tciLow\tave\tciHigh\tRelErr",file=datafile)
for n in input_list: # for each number of bins and balls
    print("Running for n=",n) # log starting a run
    out_run=run_simulator(n) # get the output results of a run
    print(*out_run,sep="\t",file=datafile) # write on a file
datafile.close() # close the file
