import random

N_values = [10,50,100,150,300,500,750,1000,1200,1500,2000,5000,10000,50000,100000]
N_values = [10,50,100,150,300,500,750,1000]

file_name = 'Results1.txt'
results = open(file_name,'w')

for n_value in N_values:
    n_runs = 0 #int(input("Please enter a n_runs (or 0 for default):\n"))
    if(n_runs == 0):
        n_runs = 20
        N = n_value
    else:
        N = int(input("Please enter a N balls:\n"))
    print(f'Simulation with n_runs= {n_runs} and N= {N}')
    seeds = range(n_runs)

    max_values = [0]*n_runs

    for r in range(n_runs):
        bins = [0]*N
        random.seed = seeds[r]
        max = 0

        for n in range(N):
            bin = random.randrange(0,N)
            bins[bin] = bins[bin]+1
            if(bins[bin]>max):
                max = bins[bin]

        max_values[r] = max

    results.write(f'{N};')
    for r in range(n_runs):
        t=''
        if(r>0):
            t=','
        t = t + str(max_values[r])
        results.write(t)
    results.write('\n')
