import numpy as np
import simpy
from scipy.stats import t

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--task', type=int, help='Number of task', choices=[1,2,3], required=False, default=1)
parser.add_argument('--servt', type=str, help='Service Time: [Exp, Uni]', choices=['Exp','Uni'], required=False, default='Exp')
parser.add_argument('--maxcap', type=int, help='Maximum system capacity (-1:np.inf)', required=False, default=-1)
parser.add_argument('--nserv', type=int, help='Number of services (>0)', required=False, default=1)
parser.add_argument('--servpoli', type=int, help='Server Policy', choices=[1,2], required=False, default=1)
args = parser.parse_args()

def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) if n_runs > 1 else 0 # std dev
	ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave if ave>0 else 0
	return ave, ci, rel_err

# ******************************************************************************
# To take the measurements
#
# Collect
# - total number of arrivals
# - total numnber of departures
# - integral of the number of client in time
# - store the time of the last event (for computing the integral)
# - total delay in the queue
# ******************************************************************************
class Measure:
	def __init__(self,Narr,Ndep,NAveraegUser,OldTimeEvent,AverageDelay):
		self.arr = Narr
		self.dep = Ndep
		self.ut = NAveraegUser
		self.oldT = OldTimeEvent
		self.delay_sys = AverageDelay
		self.delay_que = 0
		self.max_user = 0

# ******************************************************************************
# Client
#
# Identify the client with
# - type: for future use
# - time of arrival (for computing the delay, i.e., time in the queue)
# ******************************************************************************
class Client:
	def __init__(self,type,arrival_time):
		self.type = type
		self.arrival_time = arrival_time

class Server:
	def __init__(self,service_time):
		self.service_time = service_time
		self.busy = 0
		self.utilization = 0
		self.customers = 0

def GetServiceTime(service):
	if(exp_service_time):
		#Takes as input beta=1/lambda=SERVICE
		service_time = np.random.exponential(service, size=1)
	else:
		service_time =  np.random.uniform(high=service, size=1)
	# print(service_time)
	return service_time


# ******************************************************************************
# Process for the client arrivals
#
# Receive in input
# - the evnironment (simpy)
# - the queue of the clients
# ******************************************************************************
def arrival_process(environment,queue):
	global users
	global line_users

	while True:
		# cumulate statistics
		data.arr += 1
		data.ut += users*(environment.now-data.oldT)
		data.oldT = environment.now

		#Add a Client if the line is not full
		if(users<=system_capacity):
			# update the state variable, by increasing the no. of clients by 1
			users += 1
			line_users += 1
			#Store the maximum number of users
			if (users>data.max_user):
				data.max_user = users
			# create a record for the client
			client = Client(TYPE1,environment.now)

			# insert the record in the queue
			queue.append(client)

		# sample the time until the next arrival
		inter_arrival = np.random.exponential(ARRIVAL, size=1)

		if(line_users <= number_services):
			#Get the first free service
			free_servers = [x for x in servers if x.busy==0]

			#Check if at least one server is free
			if(len(free_servers)>0):
				if(server_policy==1):
					#Get random server
					index = np.random.randint(0,len(free_servers))
				elif(server_policy==2):
					#Get fastest server
					serv_times = [x.service_time for x in free_servers]
					index = np.argmin(serv_times)

				server = free_servers[index]
				#Set the server as busy
				server.busy = 1
				env.process(departure_process(env,server,queue))

		# yield to the next arrival
		yield environment.timeout(inter_arrival)

		# the execution flow will resume here
		# when the "timeout" event is executed by the "environment"
		# after a simulated time equal to inter_arrival

# ******************************************************************************
# Process for a client departure
#
# Receive in input
# - the evnironment (simpy)
# - the service time
# - the queue of the clients
# ******************************************************************************
# ******************************************************************************
def departure_process(environment,server, queue):
	global users
	global line_users

	line_users -= 1
	service = server.service_time
	service_time = GetServiceTime(service)

	# yield to the end of service
	yield environment.timeout(service_time)
	# the execution flow will resume here
	# when the "timeout" event is executed by the "environment"
	# after a simulated time equal to service_time

	server.utilization += service_time

	# get the first element from the queue
	client = queue.pop(0)

	# cumulate statistics
	data.dep += 1
	data.ut += users*(environment.now-data.oldT)
	data.oldT = environment.now
	data.delay_sys += (environment.now-client.arrival_time)
	data.delay_que += (environment.now-client.arrival_time) - service_time

	# update the state variable, by decreasing the no. of clients by 1
	users -= 1
	server.customers += 1

	# check whether there are more clients to in the queue
	if(line_users>0):
		# generate a new process for the client that starts a service
		env.process(departure_process(env,server,queue))
	else:
		server.busy = 0



# ******************************************************************************


# ******************************************************************************
# Constants
# ******************************************************************************
SIM_TIME = 200000 # condition to stop the simulation

#TASK 1
#Exponential distributed service time or
#Uniform distributed service time
exp_service_time = True if args.servt=='Exp' else False
#TASK 2
#Infinite of finete system capacity
system_capacity = np.inf if args.maxcap==-1 else args.maxcap
#TASK 3
#Multi server
number_services = args.nserv
#How to choose a server (fastest, ...)
server_policy = args.servpoli

#The task to be performed
task = args.task

confidence_level = 0.95
n_runs = 6 if server_policy==2 else 3
debug = True

# for system_capacity in [5,10,15,20]: #Semi-manual loop for task 2
# for number_services in [2,4,6,8,10]: #Semi-manual loop for task 3
if(True): #Avoid indent if the above are uncommented
	queue_file = open(f"queue{task}_{exp_service_time}_B{system_capacity}_S{number_services}_P{server_policy}.dat", "w")
	print("LOAD\tciWT\taveWT\trel_errWT\tthWT\tciLoad\taveLoad\trel_errLoad\tciLoss\taveLoss\trel_errLoss",file=queue_file)

	# Initialize the random number generator
	np.random.seed(42)

	#Not interesting result for small values of load
	if(task==1):
		loads = np.arange(0.25,1,0.05)
		loads = np.append(loads,0.98)
	elif(task==2):
		loads = np.arange(0.3,1,0.25)
		loads = np.append(loads,np.arange(1,10.01,1))
	elif(task==3):
		loads = np.arange(0.4,1.00,0.1) if exp_service_time else np.arange(0.4,2.09,0.2)
	print(loads)

	for l in loads: #[12:]
		if(task==3):
			LOAD = l * number_services  # load of the queue
		else:
			LOAD = l

		SERVICE = 10 # av service time
		ARRIVAL = SERVICE/LOAD # av. inter-arrival time
		TYPE1 = 1 # At the beginning all clients are of the same type, TYPE1

		#Coefficient of variation squared C^2_s
		if(exp_service_time):
			service_rate = 1/SERVICE #[s^-1]
			#Mean of an Exp(lambda) is 1/lambda=SERVICE
			mean_service_time = SERVICE #[s]
			coef_variation = 1
		else:
			#Mean of the Uniform(0,B) is B/2
			#In this case B=SERVICE=10
			service_rate = 1/(SERVICE/2)
			mean_service_time = SERVICE/2
			# V(U(0,B)) = 1/12 B^2
			var_service = (1.0/12.0) * SERVICE**2
			coef_variation = var_service/(mean_service_time**2)
			# print(coef_variation)

		# lambda/mu/m = LOAD
		ro = (1/ARRIVAL)/(service_rate)/number_services

		average_queue_times = np.zeros(n_runs)
		prob_losses = np.zeros(n_runs)
		average_server_util = np.zeros(n_runs)

		for r in range(n_runs):
			print(f'Load: {l}, Run: {r}')
			servers = []

			#Genarate services
			for i in range(number_services):
				if(server_policy==1):
					service = SERVICE
				elif(server_policy==2):
					#Assign services time such that the average if SERVICE (at least for large number of servers)
					service = np.random.uniform(low=SERVICE-3, high=SERVICE+3)

				servers.append(Server(service))


			# State variable: number of users
			users=0
			line_users = 0
			# the simulation time
			time = 0
			# Queue of the clients
			queue=[]
			# Collect measurements
			data = Measure(0,0,0,0,0)
			# create the environment
			env = simpy.Environment()
			# start the arrival processes
			env.process(arrival_process(env, queue))

			# simulate until SIM_TIME
			env.run(until=SIM_TIME)

			# ******************************************************************************
			# Print outputs
			# ******************************************************************************

			losses = data.arr-(data.dep+users)
			prob_losses[r] = losses/(data.arr)
			theorical_losts = data.arr * (1-ro)/(1-ro**(system_capacity+1))*(ro**system_capacity) if system_capacity<np.Inf else 0
			if(debug):
				print("\n\n\n","*"*10,"  VALUES  ","*"*10)
				print('LOAD = ',LOAD)
				print('SERVICE = ',SERVICE)
				print('ARRIVAL = ',ARRIVAL)
				print('SIM_TIME = ',SIM_TIME)
				print('exp_service_time = ',exp_service_time)
				print("*"*40)

				print("\n\n","*"*10,"  MEASUREMENTS  ","*"*10)
				print("No. of users in the queue at the end of the simulation:",users,\
						"\nTot. no. of arrivals =",data.arr,"- Tot. no. of departures =",data.dep, \
						"\nMax number of user in line =",data.max_user, \
						"\nTot no. of losts =",losses, " Theoretical no. of losts =", theorical_losts)
				print("Actual queue size: ",len(queue))
				if len(queue)>0:
					print("Arrival time of the last element in the queue:",queue[-1].arrival_time)

				print("\nLoad: ",LOAD)
				print("Nominal arrival rate: ",1/ARRIVAL)
				print("Measured arrival rate",data.arr/env.now,"\nMeasured departure rate: ",data.dep/env.now)


			#THEORETICAL NUMBER OF USERS IN THE SYSYTEM
			theorical_avg_n_user = ro * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) )
			avg_n_user = data.ut/env.now
			if(debug):
				print("\nAverage number user system\nTheorical: ", theorical_avg_n_user,"  -  Empirical: ",avg_n_user)


			#THEORETICAL TIME SPENT IN THE SYSTEM
			theorical_system_time = theorical_avg_n_user*ARRIVAL #SERVICE * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) )
			# theorical_system_time = mean_service_time * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) )
			# if(system_capacity<np.Inf):
			# 	theorical_system_time = ro/(1-ro**(system_capacity+1))*( 1 - (system_capacity+1) * ro**(system_capacity+1) )/(1-ro) / (1/ARRIVAL*(1-theorical_losts))
			if(debug):
				print("Time spent in the system \nTheorical= ",theorical_system_time,"  -  Empirical: ",data.delay_sys/data.dep)



			#THEORETICAL TIME SPENT IN THE QUEUE
			#It may happen that the
			theorical_queue_time = theorical_system_time - mean_service_time
			queue_time = data.delay_que/data.dep
			average_queue_times[r] = queue_time
			if(debug):
				print("Time spent in the queue\nTheorical: ", theorical_queue_time,"  -  Empirical: ", queue_time)


			# if(task==1):
			server_utilization = servers[0].utilization/env.now
			average_server_util[r] = server_utilization
			if(debug or task==3):
				print('\nServers utilization:')
				for i,s in enumerate(servers):
					server_utilization = s.utilization/env.now
					print(f'Server: {i}, Utilization: {server_utilization}, Customers served: {s.customers}, Service Time: {s.service_time}')
				print("*"*40)

		aveWT, ciWT, rel_errWT = evaluate_conf_interval(average_queue_times)
		aveLoad, ciLoad, rel_errLoad = evaluate_conf_interval(average_server_util)
		probLoss, ciLoss, rel_errLoss = evaluate_conf_interval(prob_losses)
		print(f'{l}\t{ciWT}\t{aveWT}\t{rel_errWT}\t{theorical_queue_time}\t{ciLoad}\t{aveLoad}\t{rel_errLoad}\t{ciLoss}\t{probLoss}\t{rel_errLoss}', file=queue_file)

			# print(f'{LOAD}\t{ci}\t{ave}\t{rel_err}', file=queue_server_file)

	queue_file.close()
	# queue_server_file.close()

import os
if(task==1):
	os.system(f'python Plot.py --task {args.task} --servt {args.servt} --maxcap {args.maxcap} --nserv {args.nserv} --servpoli {args.servpoli}')
