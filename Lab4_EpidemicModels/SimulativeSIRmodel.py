import numpy as np
import matplotlib.pyplot as plt
import pygame
import time
from scipy import spatial
from scipy.stats import t

def evaluate_conf_interval(x):
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) # std dev
	ci = t_sh * stddev / np.sqrt(n_runs) # confidence interval half width

	#print(ave, stddev, t_sh, runs, ci, ave)
	rel_err = ci / ave if ave>0 else 0
	return ave, ci, rel_err

class Individual():
	def __init__(self,id):
		#Individual ID
		self.id = id
		#Region where the Individual is (This is updated every day)
		self.region = -1
		#Cordinates (x and y) of the position
		self.pos = np.random.uniform(size=2)
		#Categories: 0:, 1:
		self.category=0
		#Number of days since the infection day
		self.day_infection = 0
		#List of all contacts
		self.contacts = []

	#Update the category with a given one
	def UpdateState(self,cat='',infection_period=0):
		if(cat != ''):
			self.category=cat
			return
		if(self.category==1):
			self.day_infection+=1
			#If the infected individual is 'ill' for infection_period days he recovers
			if(self.day_infection>infection_period):
				self.category=2
				return self.id

	#Check if an Individual is within a range distance
	def CheckDistance(self,other,distance):
		#This is a flag to understand if the infected individual infected a suceptible individual
		is_infected = False
		#3 conditions must be satisfied, given an infected individual(self,this) and individual 'other':
		#-They are 'close' enough &
		#-Category of 'other' id 0(susceptible) &
		#-It happnes that 'other' is infected by chance ('flip a coin')

		other_pos = other.pos
		#First check x distance
		x_dist = abs(self.pos[0]-other_pos[0])
		if(x_dist<=distance):
			#Then check y distance
			y_dist = abs(self.pos[1]-other_pos[1])
			if(y_dist<=distance):
				#Finally calculate the actuall distance between the 2 points. Avoid calculate the sqrt
				# dis = x_dist**2 + y_dist**2
				# if(dis<=distance**2):
					#Withing the range (Contact)
				is_infected = self.Infect(other,0.2)
		#Too far (no contacts)
		return is_infected

	def Infect(self,other,beta):
		if(other.category == 0):
			#Flip a 'coin' to infect the contact
			r = np.random.uniform()
			#print(r)
			if(r<beta):
				#infected.append(other.id)
				other.UpdateState(1)
				return True
			else: 
				return False

	#Move the Individual to a new random position
	def Move(self,range):
		direction = np.random.uniform(-range,range,2)
		pos = self.pos + direction
		#Outside the box
		if( pos[0]<0 or pos[0]>1 or pos[1]<0 or pos[1]>1 ):
			#Move towards the center
			# print(f'Outside {pos}')
			direction = (0.5,0.5) - self.pos
			pos = self.pos + np.random.uniform(0,0.3,size=2) * direction
			# print(f'New pos  {pos}')
			# time.sleep(6)
		self.pos = pos
	#Plot the Individual shape: a circle
	def PlotCircle(self,screen,screen_size):
		s = 2
		if(self.category==0):
			color = (0,120,255) #Susceptible
		elif(self.category==1):
			color = (255,0,0) #Infected
			s = 3
		elif(self.category==2):
			color = (0,255,100) #Recovered
		#Add a little shitf to the points
		pygame.draw.circle(screen, color, self.pos*screen_size, s)

	#Draw a line between this point and a destination point. One line for each contact
	def PlotLink(self,screen,screen_size):
		for c in self.contacts:
			pygame.draw.line(screen, (0,0,0), self.pos*screen_size, c.pos*screen_size)

def ReturnRegion(pos):
	#The regions are: (example number_regions=3 -> grid 3x3)
	# 0	1	2
	#	3	4	5
	#	6	7	8	
	#The formula is x+y*n
	x_region = -1
	y_region = -1
	#Sqrt of the number of regions (assuming they are a perfect square)
	n = round(number_regions)
	for x in range(number_regions):
		if(1.0/n*x<pos[0] and 1.0/n*(x+1)>=pos[0]):
			x_region = x
			break
	for y in range(number_regions):
		if(1.0/n*y<pos[1] and 1.0/n*(y+1)>=pos[1]):
			y_region = y
			break
	#Calculate the actuall region as an integer
	actuall_region = x_region + y_region * number_regions
	return actuall_region

#Small test
# print(ReturnRegion([0.01,0.01])) #expected 0
# print(ReturnRegion([0.51,0.51])) #something in the middle, like A/2 (expected 4 for A=3)
# print(ReturnRegion([0.99,0.99])) #expected A-1
#exit()

pygame.init()
screen_size = [800, 600]
screen = pygame.display.set_mode(screen_size)

###	ÌNITIAL PARAMETERS	###
#How many people there are in the population
population_size = 10000 # N
#Number of days we will consider
total_days = 365
#The number of people per day an infected person infects someone susceptible (beta) [day^-1]
transmission_rate=0.2
#The number of days an infencted person stays infeccted (gamma) [day^-1]
infection_period=14
recovery_rate=1/infection_period
#The distance an Individual can move each day
length_movement = 1/20
#The distance at which Individual can interact (contact)
concact_range = 5/1000

print('Transmission Rate: ', transmission_rate)
print('Recovery Rate: ', recovery_rate)

initial_seed = 2502
np.random.seed(initial_seed)
confidence_level = 0.95

n_runs = 3
max_infections_runs = np.zeros(n_runs)
epidemic_ends_runs = np.zeros(n_runs)

#Number of regions to divide the population in (number_regions=A -> grid AxA)
number_regions = 3
###	END INITIAL PARAMETERS	###

def Simulator(r):
	print(f"\n{'#'*5}\tStarting Run: {r}\t{'#'*5}")

	#Individuals
	population = [Individual(i) for i in range(population_size)]

	#List with all infected people indeces. This is used for optimization purposes
	infected_individuals = set()

	#Initial conditions (day 0)
	first_infected = np.random.randint(population_size)
	print(f'First infected: {first_infected}')
	population[first_infected].UpdateState(1)
	infected_individuals.add(first_infected)

	end_epidemic = total_days-1

	S = np.zeros(total_days, dtype=int) #Susceptible
	I = np.zeros(total_days, dtype=int) #Infected
	R = np.zeros(total_days, dtype=int) #Recovered

	#Initial conditions (day 0)
	S[0] = population_size - 1
	I[0] = 1
	R[0] = 0
	max_infections = 1

	tt_init = time.time()
	#Skip the day 0
	for d in range(1,total_days):
		new_infected = 0
		new_recovered = 0
		# print('Day ',d)
		ti = time.time()
		screen.fill((255, 255, 255))

		individuals_per_regions = {}
		for i in range(number_regions**2):
			individuals_per_regions[i] = []
		for p in population: 
			region = ReturnRegion(p.pos)
			individuals_per_regions[region].append(p.id)
			p.region = region

		#Loop over all the population
		for p in population:
			#Draw the Individual at its position
			p.PlotCircle(screen,screen_size)
		te_plot = time.time()
		# print(f'Plotting Time: {(te_plot-ti):.2f}')

		current_infections = list(infected_individuals)
		#Loop over all the infected individual. m<N
		for inf_indi in current_infections:
			infected_region = population[inf_indi].region
			population_in_region = individuals_per_regions[infected_region]
			# Loop over all the population
			for pop_index in population_in_region:
				if(inf_indi is not pop_index):
					#Calcaulate the distance between the two points: i and j
					ii = population[inf_indi].CheckDistance(population[pop_index],concact_range)
					if(ii):
						infected_individuals.add(pop_index)
						new_infected += 1

			#Plot the edge between the infected and all its contacts (Too many points)	
			#population[inf_indi].PlotLink(screen,screen_size)
			
			recovered = population[inf_indi].UpdateState(infection_period=infection_period)
			if(recovered != None):
				infected_individuals.remove(recovered)
				new_recovered += 1

		te = time.time()
		# print(f'Checking Distance Time: {(te-te_plot):.2f}')

		for p in population:
			#Move the points for the next day
			p.Move(length_movement)

		S[d] = S[d-1] - new_infected
		I[d] = I[d-1] + new_infected - new_recovered
		R[d] = R[d-1] + new_recovered

		# print(f'Situation: S: {S[d]}, I: {I[d]}, R: {R[d]}, Total: {S[d]+I[d]+R[d]}')
		if(I[d]<1):
			end_epidemic = d
			break

		pygame.display.flip()
		pygame.display.update()
		#time.sleep(.01)

	tt_end = time.time()
	print(f'Run: {r},Total time: {(tt_end-tt_init):.2f}')

	print(f'Epidemic ended at day: {end_epidemic}')
	print(f'End situation: S: {S[end_epidemic]}, I: {I[end_epidemic]}, R: {R[end_epidemic]}')

	plt.figure(figsize=(12, 6), dpi=80)
	days = range(end_epidemic)
	S = S[:end_epidemic]
	I = I[:end_epidemic]
	R = R[:end_epidemic]
	plt.plot(days,S, label='Susceptible')
	plt.plot(days,I, label='Infected')
	plt.plot(days,R, label='Recovered')


	title = 'Numeric SIR Model'	
	plt.title(title)
	plt.legend(loc='center right')
	plt.xlabel('Days')
	plt.ylabel('Number People')

	#Expected number of people the first infected individual will infect (Beta/gamma)
	R0 = transmission_rate/recovery_rate
	print(f'R0 value: {R0}')

	#Max number of infections and the day when this happens
	day_max_infections = np.argmax(I)
	max_infections = int(I[day_max_infections])
	print(f'Max Infections: {max_infections}, day at which occurs: {day_max_infections}')
	print(f"{'#'*5}\tEnding Run: {r}\t{'#'*5}")

	#plt.show()
	title = title.replace(' ','')
	save_title = (f'Images/{title}{r}')
	plt.savefig(save_title)

	return max_infections, end_epidemic

for r in range(n_runs):
	max_inf, end_epi = Simulator(r)

	max_infections_runs[r] = max_inf
	epidemic_ends_runs[r] = end_epi

datafile = open(f"simulativeSIRmodel.dat", "w")
print("maxInfections\tave\tci\trel_err",file=datafile)
ave, ci, rel_err = evaluate_conf_interval(max_infections_runs)
print(f"1\t{ave}\t{ci}\t{rel_err}",file=datafile)
print(f"1\t{ave}\t{ci}\t{rel_err}")
ave, ci, rel_err = evaluate_conf_interval(epidemic_ends_runs)
print(f"0\t{ave}\t{ci}\t{rel_err}",file=datafile)
print(f"0\t{ave}\t{ci}\t{rel_err}")

pygame.quit()