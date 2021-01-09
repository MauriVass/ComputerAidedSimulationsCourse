
import numpy as np
import simpy
from scipy.stats import t

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
		self.delay = AverageDelay
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
	if(exp_arrival_time):
		service_time = np.random.exponential(service, size=1)
	else:
		service_time = np.random.uniform(high=service, size=1)
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
		if(len(queue)<line_capacity):
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

		if(users <= number_services):
			#Get the first free service
			free_servers = [x for x in servers if x.busy==0]
			# print(free_servers)
			# t.sleep(1)
			#Check if at least one server is free
			if(len(free_servers)>0):
				server = free_servers[0] #index_services[something]
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
	server.utilization += service_time
	# yield to the end of service
	yield environment.timeout(service_time)
	# the execution flow will resume here
	# when the "timeout" event is executed by the "environment"
	# after a simulated time equal to service_time

	# get the first element from the queue
	# client=queue.pop() #(pop?)
	client = queue.pop(0)

	# cumulate statistics
	data.dep += 1
	data.ut += users*(environment.now-data.oldT)
	data.oldT = environment.now
	data.delay += (environment.now-client.arrival_time)

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

confidence_level = 0.95
n_runs = 1
debug = True
task = 1

queue_time_file = open(f"queuesystem1_queuetime.dat", "w")
print("LOAD\tci\tave\trel_err\tthTime",file=queue_time_file)
queue_server_file = open(f"queuesystem1_serverload.dat", "w")
print("LOAD\tci\tave\trel_err\tthService",file=queue_server_file)

# Initialize the random number generator
np.random.seed(42)
#Not interesting result for small values of load
loads = np.arange(0.2,1,0.05)
print(loads)
for l in loads[12:13]:
	LOAD = 0.85  # load of the queue

	#For task 1
	average_queue_times = np.zeros(n_runs)
	average_server_util = np.zeros(n_runs)

	for r in range(n_runs):
		print(f'Load: {l}, Run: {r}')
		number_services = 1
		servers = []
		SERVICE = 10 # av service time
		#Get services time form an uniform distribution around SERVICE time
		#services = np.random.uniform(low=SERVICE-2, high=SERVICE+2, size=number_services)
		#Set manually to have more control
		for i in range(number_services):
			servers.append(Server(SERVICE))

		ARRIVAL = SERVICE/LOAD # av. inter-arrival time
		TYPE1 = 1 # At the beginning all clients are of the same type, TYPE1

		SIM_TIME = 500000 # condition to stop the simulation

		exp_arrival_time = True
		system_capacity = np.inf
		line_capacity = system_capacity - number_services

		# ******************************************************************************
		# Initialization
		# ******************************************************************************
		#

		#arrivals=0
		# State variable: number of users
		users=0
		line_users = 0
		# the simulation time
		time = 0
		# Queue of the clients
		queue=[]
		# Collect measurements
		data = Measure(0,0,0,0,0)
		# Initialize the random number generator
		# np.random.seed(42)
		# create the environment
		env = simpy.Environment()
		# start the arrival processes
		env.process(arrival_process(env, queue))


		# simulate until SIM_TIME
		env.run(until=SIM_TIME)

		# ******************************************************************************
		# Print outputs
		# ******************************************************************************

		#Coefficient of variation squared C^2_s
		if(exp_arrival_time):
			mean_service = 1/SERVICE
			coef_variation = 1
		else:
			mean_service = SERVICE/2
			var_service = (1.0/12.0) * SERVICE**2
			coef_variation = var_service/mean_service**2 #0
			print(coef_variation)
		# lambda/mu = LOAD
		ro = LOAD
		# print("No. of users in the queue at the end of the simulation:",users,\
		# 			"\nTot. no. of arrivals =",data.arr,"- Tot. no. of departures =",data.dep, \
		# 			"\nMax number of user in line =",data.max_user,
		# 			"\nTot no. of losts =",data.arr-data.dep-users)
		if(debug):
			print("\n\n\n","*"*10,"  VALUES  ","*"*10)
			print('LOAD = ',LOAD)
			print('SERVICE = ',SERVICE)
			print('ARRIVAL = ',ARRIVAL)
			print('SIM_TIME = ',SIM_TIME)
			print('exp_arrival_time = ',exp_arrival_time)
			print('line_capacity = ',line_capacity)
			print("*"*40)

			print("\n\n","*"*10,"  MEASUREMENTS  ","*"*10)
			theorical_losts = data.arr * (1-ro)/(1-ro**(system_capacity+1))*(ro**system_capacity) if system_capacity<np.Inf else 0
			print("No. of users in the queue at the end of the simulation:",users,\
					"\nTot. no. of arrivals =",data.arr,"- Tot. no. of departures =",data.dep, \
					"\nMax number of user in line =",data.max_user, \
					"\nTot no. of losts =",data.arr-data.dep-users, " Theoretical no. of losts =", theorical_losts)
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
		# theorical_system_time = mean_service * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) )
		if(system_capacity<np.Inf):
			theorical_system_time = ro/(1-ro**(system_capacity+1))*( 1 - (system_capacity+1) * ro**(system_capacity+1) )/(1-ro) / (1/ARRIVAL*(1-theorical_losts))
		if(debug):
			print("Time spent in the system \nTheorical= ",theorical_system_time,"  -  Empirical: ",data.delay/data.dep)



		#THEORETICAL TIME SPENT IN THE QUEUE
		theorical_num_user_queue = ro**2 / (1-ro)
		theorical_queue_time = theorical_num_user_queue*ARRIVAL #ro * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) )
		# theorical_queue_time = mean_service * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) )
		# theoretical_avg_n_user = data.ut/env.now
		queue_time = data.delay/data.dep - SERVICE
		average_queue_times[r] = queue_time
		if(debug):
			print("Time spent in the queue\nTheorical: ", theorical_queue_time,"  -  Empirical: ", queue_time)


		if(task==1):
			server_utilization = servers[0].utilization/env.now
			average_server_util[r] = server_utilization
		if(debug):
			print('\nServers utilization:')
			for i,s in enumerate(servers):
				server_utilization = s.utilization/env.now
				print(f'Server: {i}, Utilization: {server_utilization}, Customers served: {s.customers}, Service Time: {s.service_time}')
			print("*"*40)

	if(task==1):		
		ave, ci, rel_err = evaluate_conf_interval(average_queue_times)
		print(f'{LOAD}\t{ci}\t{ave}\t{rel_err}\t{theorical_queue_time}', file=queue_time_file)

		ave, ci, rel_err = evaluate_conf_interval(average_server_util)
		print(f'{LOAD}\t{ci}\t{ave}\t{rel_err}', file=queue_server_file)

queue_time_file.close()
queue_server_file.close()

import os
if(n_runs>1):
	os.system(f'python Plot.py')
