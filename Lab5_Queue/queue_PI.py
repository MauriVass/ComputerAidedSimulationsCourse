
import numpy as np
import simpy
import time as t

# ******************************************************************************
# Constants
# ******************************************************************************
number_services = 1
LOAD = 0.85  # load of the queue
SERVICE = 10 # av service time
services = np.random.uniform(low=SERVICE, high=SERVICE, size=number_services)
free_services = np.zeros(number_services, dtype=np.int8)

ARRIVAL = SERVICE/LOAD # av. inter-arrival time
TYPE1 = 1 # At the beginning all clients are of the same type, TYPE1

LAMBDA = 1/ARRIVAL
MU = 1/SERVICE

SIM_TIME = 500000 # condition to stop the simulation

exp_arrival_time = True
line_capacity = 42 #10000 * ARRIVAL

print(number_services,services,np.mean(services),ARRIVAL)
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


def GetServiceTime(service):
	if(exp_arrival_time):
		service_time = np.random.exponential(service, size=1)
	else:
		service_time = 1/MU #random.uniform(a=0,b=1/MU)
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
			index_services = np.where(free_services==0)[0]
			# print(free_services,index_services,index_services.size)
			# t.sleep(1)
			#Check if at least one server is free
			if(index_services.size>0):
				index_service = free_services[0]
				#Set the server as busy
				free_services[index_service] = 1
				env.process(departure_process(env,index_service,queue))

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
def departure_process(environment,index_service, queue):
	global users
	global line_users

	line_users -= 1
	service = services[index_service]
	service_time = GetServiceTime(service)
	# yield to the end of service
	yield environment.timeout(service_time)
	# the execution flow will resume here
	# when the "timeout" event is executed by the "environment"
	# after a simulated time equal to service_time

	# get the first element from the queue
	client=queue.pop()

	# cumulate statistics
	data.dep += 1
	data.ut += users*(environment.now-data.oldT)
	data.oldT = environment.now
	data.delay += (environment.now-client.arrival_time)

	# update the state variable, by decreasing the no. of clients by 1
	users -= 1

	# check whether there are more clients to in the queue
	if(line_users>0):
		# generate a new process for the client that starts a service
		env.process(departure_process(env,index_service,queue))
	else:
		free_services[index_service] = 0



# ******************************************************************************

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
np.random.seed(42)
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
	coef_variation = 1
else:
	coef_variation = 0
# lambda/mu = LOAD
ro = LAMBDA/MU

print("\n","*"*10,"  VALUES  ","*"*10)
print('LOAD = ',LOAD)
print('SERVICE = ',SERVICE)
print('ARRIVAL = ',ARRIVAL)
print('TYPE1 = ',TYPE1)
print('LAMBDA = ',LAMBDA)
print('MU = ',MU)
print('SIM_TIME = ',SIM_TIME)
print('exp_arrival_time = ',exp_arrival_time)
print('line_capacity = ',line_capacity)
print("*"*40)

print("\n\n","*"*10,"  MEASUREMENTS  ","*"*10)
print("No. of users in the queue at the end of the simulation:",users,\
		"\nTot. no. of arrivals =",data.arr,"- Tot. no. of departures =",data.dep, \
		"\nMax number of user in line =",data.max_user,
		"\nTot no. of losts =",data.arr-data.dep-users)
print("Actual queue size: ",len(queue))
if len(queue)>0:
	print("Arrival time of the last element in the queue:",queue[-1].arrival_time)

print("\nLoad: ",LOAD)
print("Nominal arrival rate: ",LAMBDA)
print("Measured arrival rate",data.arr/env.now,"\nMeasured departure rate: ",data.dep/env.now)

#Theoretical time spent in the queue
theorical_queue_time = ro * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) ) #(LAMBDA)/(MU-LAMBDA)
#print("\n\nAverage number of users\nTheorical: ", theorical_queue_time,"  -  Empirical: ",data.ut/env.now)
print("\nTime spent in the queue\nTheorical: ", theorical_queue_time,"  -  Empirical: ",data.ut/env.now)

#Theoretical time spent in the system
theorical_system_time = 1/MU * ( 1 + ro * (1+coef_variation)/(2*(1-ro)) ) #1.0/(MU-LAMBDA)
#print("Average delay \nTheorical= ",theorical_system_time,"  -  Empirical: ",data.delay/data.dep)
print("Time spent in the system \nTheorical= ",theorical_system_time,"  -  Empirical: ",data.delay/data.dep)

# #print("Average delay \nTheorical= ",theorical_system_time,"  -  Empirical: ",data.delay/data.dep)
# print("Time spent in the service \nTheorical= ",theorical_system_time-theorical_queue_time,"  -  Empirical: ",data.delay/data.dep-data.ut/env.now)

print("*"*40)
