import numpy as np
import matplotlib.pyplot as plt
print('Loading pygame....')
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
		#Categories: s:Susceptible, i:Infected, r:Recovered
		self.category= 's'
		#Number of days since the infection day
		self.day_infection = 0
		#Number of infections
		self.infections = 0

	#Update the category with a given one
	def UpdateState(self,infection_period=0):
		if(self.category=='i'):
			self.day_infection+=1
			#If the infected individual is 'ill' for infection_period days he recovers
			if(self.day_infection>infection_period):
				self.category='r'
				return self.id

	#Check if an Individual is within a range distance
	def CheckDistance(self,other,distance,beta):
		#This is a flag to understand if the infected individual infected a suceptible individual
		is_infected = False
		#3 conditions must be satisfied, given an infected individual(self,this) and individual 'other':
		#-They are 'close' enough &
		#-Category of 'other' id is 0(susceptible) &
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
				# self.contacts += 1
				is_infected = self.Infect(other,beta)
		#Too far (no contacts)
		return is_infected

	def Infect(self,other,beta):
		if(other.category == 's'):
			#Flip a 'coin' to infect the contact
			r = np.random.uniform()
			if(r<beta):
				self.infections += 1
				other.category='i'
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
			direction = (0.5,0.5) - self.pos
			pos = self.pos + np.random.uniform(0,0.1,size=2) * direction

			#Just clip the position between [0,1]
			# padding = 0.005
			# pos[0] = np.clip(pos[0],0+padding,1-padding)
			# pos[1] = np.clip(pos[1],0+padding,1-padding)
		self.pos = pos
	#Plot the Individual shape: a circle
	def PlotCircle(self,screen,screen_size):
		s = 2
		if(self.category=='s'):
			color = (0,120,255) #Susceptible
		elif(self.category=='i'):
			color =  (255,0,0) #Infected
		elif(self.category=='r'):
			color = (50,205,50) #Recovered
		#Add a little shitf to the points
		pygame.draw.circle(screen, color, self.pos*screen_size, s)

	#Draw a line between this point and a destination point. One line for each contact (To be refactored)
	def PlotLink(self,screen,screen_size):
		for c in self.contacts:
			pygame.draw.line(screen, (0,0,0), self.pos*screen_size, c.pos*screen_size)

def ReturnRegion(pos):
	#The regions are: (example number_regions=3 -> grid 3x3)
	# 	0	1	2
	#	3	4	5
	#	6	7	8	
	#The formula is x+y*number_regions
	x_region = 0
	y_region = 0
	for x in range(number_regions):
		if(1.0/number_regions*x<pos[0] and 1.0/number_regions*(x+1)>=pos[0]):
			x_region = x
			break
	for y in range(number_regions):
		if(1.0/number_regions*y<pos[1] and 1.0/number_regions*(y+1)>=pos[1]):
			y_region = y
			break
	#Calculate the actuall region as an integer
	actuall_region = x_region + y_region * number_regions
	return actuall_region
# Small test
# number_regions = 3
# print(ReturnRegion([0,0])) #expected 0
# print(ReturnRegion([0.51,0.51])) #something in the middle, like A^2/2 (expected 4 for A=3)
# print(ReturnRegion([1,1])) #expected A^2-1
# exit()

pygame.init()
screen_size = [800, 600]
screen = pygame.display.set_mode(screen_size)

###	ÌNITIAL PARAMETERS	###
#How many people there are in the population
population_size = 10000 # N
#Number of days we will consider
total_days = 365
#The number of people per day an infected person infects someone susceptible 
transmission_rate=0.2 #(beta) [day^-1]
#The number of days an infencted person stays infected 
infection_period=14
recovery_rate=1/infection_period #(gamma) [day^-1]
#Expected number of people the first infected individual will infect (Beta/gamma)
R0 = transmission_rate/recovery_rate

#The distance an Individual can move each day
#To have an idea if 1 is 5km (a small city, with 10k abitants) each individual can move in each direction of a distance of 500m
length_movement = 1/15
#The distance at which Individual can interact (contact)
#With the same numbers above, a contact is 'experienced' when 2 people are closer than 20mt
contact_range = 4/1000
# ^^^ This may not be accurate but it is just to give some meaning to these variables ^^^

print('Transmission Rate: ', transmission_rate)
print('Recovery Rate: ', recovery_rate)
print('R0 value: ', R0)

initial_seed = 2502
np.random.seed(initial_seed)
confidence_level = 0.95

n_runs = 7
max_infections_runs = np.zeros(n_runs)
max_infections_day_runs = np.zeros(n_runs)
epidemic_ends_runs = np.zeros(n_runs)

#Number of regions to divide the population in (number_regions=A -> grid AxA, A^2 regions)
number_regions = 3
#This parameter seems to work fine. Some results:
'''
number_regions = 1
Run: 0,Total time: 1060.02
Epidemic ended at day: 294
End situation: S: 2247, I: 0, R: 7753
Max Infections: 2301, day at which occurs: 135

number_regions = 2
Run: 0,Total time: 314.28
Epidemic ended at day: 242
End situation: S: 2199, I: 0, R: 7801
Max Infections: 2320, day at which occurs: 133

number_regions = 3
Run: 0,Total time: 124.08
Epidemic ended at day: 230
End situation: S: 2313, I: 0, R: 7687
Max Infections: 2191, day at which occurs: 132
'''
#The time for the execution of 1 run decrease than a factor ~1/3 increasing the number_regions by 1
#Dividing the population in regions add an approximations,
#since 2 persons in 2 different regions but close enough(dist<concact_range) can not be infected
#Also the difference between values(Max Infections,...) is not too much(they are affected by randomicity) but the speed up is significant
###	END INITIAL PARAMETERS	###

def Simulator(r):
	print(f"\n{'#'*5}\tStarting Run: {r}\t{'#'*5}")

	#Individuals
	population = [Individual(i) for i in range(population_size)]

	#List with all infected people indeces. This is used for optimization purposes (i<N)
	infected_individuals = set()

	#Initial conditions (day 0)
	first_infected = np.random.randint(population_size)
	# print(f'First infected index: {first_infected}')
	population[first_infected].category = 'i'
	infected_individuals.add(first_infected)

	S = np.zeros(total_days, dtype=int) #Susceptible
	I = np.zeros(total_days, dtype=int) #Infected
	R = np.zeros(total_days, dtype=int) #Recovered
	Rt = np.zeros(total_days) #Rt daily value

	S[0] = population_size - 1
	I[0] = 1
	max_infections = 1
	R[0] = 0
	# Rt[0] = R0

	tt_init = time.time()
	#The days are in range [0,total_days-1]
	#In the worst case the pandemic ends at the end of the simulation
	end_epidemic = total_days-1
	for d in range(0,total_days-1):
		new_infected = 0
		new_recovered = 0
		print('Day ',d,end='\r')
		ti = time.time()
		screen.fill((255, 255, 255))

		#Dictionary with: 
		#		key: the number of the region
		#		value: a set with all the Susceptible individuals in that region
		individuals_per_regions = {}
		for i in range(number_regions**2):
			individuals_per_regions[i] = set()
		#Loop over all the population
		for p in population:
			#Move the points for the next day
			p.Move(length_movement)
			#Draw the Individual at its position
			p.PlotCircle(screen,screen_size)

			#Find the regions for Susceptible and Infected people
			if(p.category!='r'):
				#Get the belonging region
				region = ReturnRegion(p.pos)
				if(p.category=='s'):
					#Add it to the dict only if is a Susceptible
					individuals_per_regions[region].add(p.id)
				else:
					#Update the infected's region
					p.region = region

		te_plot = time.time()

		#Store a temponary variable since infected_individuals is changed during the loop
		current_infections = list(infected_individuals)
		#Loop over all the infected individual. m<N
		for inf_indi in current_infections:
			#Get the region of the current infected individual
			infected_region = population[inf_indi].region
			#Get the list of the susceptible pp in the infected_region
			population_in_region = individuals_per_regions[infected_region]
			# Loop over all the individuals in the infected_region
			for pop_index in population_in_region:
				#Calcaulate the distance between the two points: i and j
				infected = population[inf_indi].CheckDistance(population[pop_index],contact_range,transmission_rate)
				if(infected):
					infected_individuals.add(pop_index)
					new_infected += 1

			#Plot the edge between the infected and all its contacts (Too many points!!) 
			#population[inf_indi].PlotLink(screen,screen_size)
			
			#For each infected individual, evaluate if he has spent more than infection_period days -> he recovered
			#This returns the ID of the individual if he recovered or nothing (None)
			recovered = population[inf_indi].UpdateState(infection_period=infection_period)
			if(recovered != None):
				infected_individuals.remove(recovered)
				new_recovered += 1

		te = time.time()
		# print(f'Checking Distance Time: {(te-te_plot):.2f}')

		#The future(tomorrow, d+1) states depends on the number on the number of new infections and recovers(today, d)
		S[d+1] = S[d] - new_infected
		I[d+1] = I[d] + new_infected - new_recovered
		R[d+1] = R[d] + new_recovered

		cum_infections = 0
		n_infected = len(current_infections)
		for i in current_infections:
			cum_infections += population[i].infections
		# print(float(cum_infections),float(n_infected),float(cum_infections) / float(n_infected))
		Rt[d+1] = float(cum_infections) / float(n_infected)

		# print(f'Situation: S: {S[d]}, I: {I[d]}, R: {R[d]}, Total: {S[d]+I[d]+R[d]}')
		if(I[d+1]<1):
			end_epidemic = d + 1
			break

		pygame.display.flip()
		pygame.display.update()
		#time.sleep(.01)

	tt_end = time.time()
	print(f'Run: {r},Total time: {(tt_end-tt_init):.2f}')

	print(f'Epidemic ended at day: {end_epidemic}')
	print(f'End situation: S: {S[end_epidemic]}, I: {I[end_epidemic]}, R: {R[end_epidemic]}')

	#Max number of infections and the day when this happens
	day_max_infections = np.argmax(I)
	max_infections = int(I[day_max_infections])
	print(f'Max Infections: {max_infections}, day at which occurs: {day_max_infections}')
	print(f"{'#'*5}\tEnding Run: {r}\t{'#'*5}")

	fig1, ax1 = plt.subplots(figsize=(12, 6), dpi=80)
	days = range(end_epidemic)
	S = S[:end_epidemic]
	I = I[:end_epidemic]
	R = R[:end_epidemic]
	ax1.plot(days,S, label='Susceptible')
	ax1.plot(days,I, label='Infected')
	ax1.plot(days,R, label='Recovered')

	title = 'Simulative SIR Model'	
	ax1.set_title(title)
	ax1.legend(loc='center right')
	ax1.set_xlabel('Days')
	ax1.set_ylabel('Number People')

	# plt.show()
	title = title.replace(' ','')
	save_title = (f'Images/{title}{r}')
	fig1.savefig(save_title)

	fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=80)
	Rt = Rt[:end_epidemic]
	ax2.plot(days,Rt, label='Rt')
	title = 'Simulative SIR Model (Rt)'	
	ax2.set_title(title)
	ax2.legend(loc='center right')
	ax2.set_xlabel('Days')
	ax2.set_ylabel('Rt')

	# plt.show()
	title = title.replace(' ','')
	save_title = (f'Images/{title}{r}')
	fig2.savefig(save_title)

	return max_infections, day_max_infections, end_epidemic

for r in range(n_runs):
	max_inf, max_day, end_epi = Simulator(r)

	#Check for not degenerate result
	if(max_day<20):
		max_infections_runs[r] = max_inf
		max_infections_day_runs[r] = max_day
		epidemic_ends_runs[r] = end_epi
	else:
		print('DEGENERATE ', i)

maxInfectionsfile = open(f"simulativeSIRmodelMaxInf.dat", "w")
print("ave\tci\trel_err",file=maxInfectionsfile)
ave, ci, rel_err = evaluate_conf_interval(max_infections_runs)
print(f"{ave}\t{ci}\t{rel_err}",file=maxInfectionsfile)
print(f"maxInfections: {ave}\t{ci}\t{rel_err}")

maxDayInfectionsfile = open(f"simulativeSIRmodelMaxDayInf.dat", "w")
print("ave\tci\trel_err",file=maxDayInfectionsfile)
ave, ci, rel_err = evaluate_conf_interval(max_infections_day_runs)
print(f"{ave}\t{ci}\t{rel_err}",file=maxDayInfectionsfile)
print(f"maxDayInfections: {ave}\t{ci}\t{rel_err}")

epidemicEndfile = open(f"simulativeSIRmodelEpicEnd.dat", "w")
print("ave\tci\trel_err",file=epidemicEndfile)
ave, ci, rel_err = evaluate_conf_interval(epidemic_ends_runs)
print(f"{ave}\t{ci}\t{rel_err}",file=epidemicEndfile)
print(f"epidemicEnd: {ave}\t{ci}\t{rel_err}")

pygame.quit()