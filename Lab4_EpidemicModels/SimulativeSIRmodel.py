import numpy as np
import matplotlib.pyplot as plt
print('Loading pygame....')
import pygame
import time
from scipy.stats import t
import random

def evaluate_conf_interval(x):
	n_runs = len(x)
	x = np.array(x)
	t_sh = t.ppf((confidence_level + 1) / 2, df=n_runs - 1) # threshold for t_student

	ave = x.mean() # average
	stddev = x.std(ddof=1) if n_runs>1 else 0 # std dev
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
		#Number of day when infection happened
		#This means that he will start infecting others from the day: self.day_infection+1
		self.day_infection = 0
		#Number of day when infection ended
		self.end_infection = 0
		#Number of infections per day. This will be a numpy array of length=self.end_infection-self.day_infection
		self.daily_infections = -1

	#Update the category with a given one
	def UpdateState(self,day):
		if(self.category=='i'):
			#If the infected individual is 'ill' for infection_period days he recovers
			if(day>self.end_infection):
				self.category='r'
				return self.id

	#Check if an Individual is within a range distance
	def CheckDistance(self,day,other,distance,beta,gamma):
		#This is a flag to understand if the infected individual infected a suceptible individual
		is_infected = False
		#3 conditions must be satisfied, given an infected individual(self,this) and individual 'other':
		#-They are 'close' enough &
		#-Category of 'other' id is s(susceptible) &
		#-It happens that 'other' is infected by chance ('flip a coin')

		other_pos = other.pos
		# First check x distance
		x_dist = abs(self.pos[0]-other_pos[0])
		if(x_dist<=distance):
			#Then check y distance
			y_dist = abs(self.pos[1]-other_pos[1])
			if(y_dist<=distance):
				#Finally calculate the actuall distance between the 2 points. Avoid calculate the sqrt
				dis = x_dist**2 + y_dist**2
				if(dis<=distance**2):
					# Withing the range (Contact)
					is_infected = self.Infect(day,other,beta,gamma)
		#Checking first x distance, then y distance and finally the actuall distance is much faster than checking directly the actuall distance

		# if(abs(self.pos[0]-other_pos[0])**2 + abs(self.pos[1]-other_pos[1])**2<=distance**2):
		# 	is_infected = self.Infect(day,other,beta,gamma)

		return is_infected

	def Infect(self,day,other,beta,gamma):
		if(other.category == 's'):
			#Flip a 'coin' to infect the contact
			r = np.random.uniform()
			if(r<beta):
				#Being infected on day i he can infect from day i+1
				#The first element of the array is: day-(i+1), with day=i+1 (the day after infection happened)
				self.daily_infections[day-(self.day_infection+1)] += 1
				other.Infected(day,gamma)
				return True
			else: 
				return False
		else:			
			return False

	def Infected(self, day, gamma):
		self.category='i'
		self.day_infection = day		
		#Choose a random number for the recovery
		#Geometric distribution G(x,p), E(x) = 1/p = 14 -> recovery average of 14 days 
		self.end_infection = int(day + np.random.geometric(gamma, size=1))
		self.daily_infections = np.zeros(self.end_infection-self.day_infection)
		# print(self.day_infection,self.end_infection,self.end_infection-self.day_infection)

	def GetNumInfections(self,day):
		# diff_left 	= day - self.day_infection
		# diff_right	= self.end_infection - day
		# if(diff_left>=0 and diff_right>=0):
		# 	# print(self.day_infection,day,self.end_infection, len(self.daily_infections), np.sum( self.daily_infections[ diff_left: ] ))
		# 	# print(self.daily_infections)
		# 	# exit()
		# 	return np.sum( self.daily_infections[ max(self.day_infection,day):min(self.end_infection,day) ] )
		# else:
		# 	#Out of window
		# 	#Returns false instead of 0 since np.sum(...) can be 0 too
		# 	return -1
		diff_left 	= day - (self.day_infection + 1)
		diff_right	= self.end_infection - day
		if(diff_right>=0): #day<self.end_infection diff_left>=0 and 
			# print(self.day_infection,day,self.end_infection, len(self.daily_infections), np.sum( self.daily_infections[ diff_left: ] ))
			# print(self.daily_infections)
			# exit()
			# print(len(self.daily_infections),max(0,day))
			s = np.sum( self.daily_infections[ max(0,diff_left): ] )
			return s
		else:
			#Out of window
			#Returns false instead of 0 since np.sum(...) can be 0 too
			return -1

	#Move the Individual to a new random position
	def Move(self,range):
		direction = np.random.uniform(-range,range,2)
		pos = self.pos + direction
		#Outside the box
		if( pos[0]<0 or pos[0]>1 or pos[1]<0 or pos[1]>1 ):
			#Move towards the center
			direction = (0.5,0.5) - self.pos
			pos = self.pos + np.random.uniform(0,0.15,size=2) * direction

			#Just clip the position between [0,1] (not a nice visual effect)
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
			s = 3.5
		elif(self.category=='r'):
			color = (50,205,50) #Recovered
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

debug = False

x = 450
y = 40
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

pygame.init()
screen_size = [800, 600]
screen = pygame.display.set_mode(screen_size)

###	INITIAL PARAMETERS	###
#How many people there are in the population
population_size = 10000 # N
#Number of days we will consider
total_days = 365
#The number of people per day an infected person infects someone Susceptible 
transmission_rate=0.2 #(beta) [day^-1]
#The number of days an infencted person stays infected 
infection_period=14
recovery_rate=1/infection_period #(gamma) [day^-1]

extension = True
if(extension):
	#The distance an Individual can move each day
	#To have an idea if 1 is 5km (a small city, with 10k abitants) each individual can move in each direction of a distance of 500m
	length_movement = 1/10
	#The distance at which Individual can interact (contact)
	#With the same numbers above, a contact is 'experienced' when 2 people are closer than 20mt
	contact_distance = 6/1000
	# ^^^ This may not be accurate but it is just to give a meaning to these variables ^^^
else:
	#In the simple SIR model there is no notion of spatiality (and distance)
	#So length_movement is set for semplicity (it actually would not change the result)
	#contact_distance is set to 1 since an Infected individual can infect a Susceptible individual to any distance
	length_movement = 0
	contact_distance = 1

print('Transmission Rate: ', transmission_rate)
print('Recovery Rate: ', recovery_rate)

initial_seed = 2505
np.random.seed(initial_seed)
confidence_level = 0.95

n_runs = 1 #7
max_infections_runs 	= [] #np.zeros(n_runs)
max_infections_day_runs = [] #np.zeros(n_runs)
epidemic_ends_runs 		= [] #np.zeros(n_runs)

#Number of regions to divide the population in (number_regions=A -> grid AxA, A^2 regions)
if(extension):
	number_regions = 3
#Since there is no notion of spatiality it make no sense to divide the population in regions in the simple SIR model

#This parameter seems to work fine. Some results:
'''
number_regions = 1
Run: 0,Total time: 1060.02 (around 18 min)
Epidemic ended at day: 294
End situation: S: 2247, I: 0, R: 7753
Max Infections: 2301, day at which occurs: 135

number_regions = 2
Run: 0,Total time: 314.28 (around 5 min)
Epidemic ended at day: 242
End situation: S: 2199, I: 0, R: 7801
Max Infections: 2320, day at which occurs: 133

number_regions = 3
Run: 0,Total time: 124.08 (around 2 min)
Epidemic ended at day: 230
End situation: S: 2313, I: 0, R: 7687
Max Infections: 2191, day at which occurs: 132
'''
#The time for the execution of 1 run decrease than a factor ~1/3 increasing the number_regions by 1
#Dividing the population in regions add an approximation,
#since 2 persons in 2 different regions (e.g. at the edge) but close enough(dist<concact_range) can not be infected,
#Also the difference between statistics(Max Infections,...) is not too much(the results are also affected by randomicity) but the speed up is significant!
###	END INITIAL PARAMETERS	###

def Simulator(r):
	print(f"{'#'*5}\tStarting Run: {r}\t{'#'*5}")

	#Individuals
	population = [Individual(i) for i in range(population_size)]

	#List with all infected people indeces. This is used for optimization purposes (i<N)
	infected_individuals = set()

	#Initial conditions (day 0)
	first_infected = np.random.randint(population_size)
	if(debug):
		print(f'First infected index: {first_infected}')
	# population[first_infected].category = 'i'
	population[first_infected].Infected(0,recovery_rate)
	infected_individuals.add(first_infected)

	S = np.zeros(total_days, dtype=int) #Susceptible
	I = np.zeros(total_days, dtype=int) #Infected
	R = np.zeros(total_days, dtype=int) #Recovered
	# Rt = np.zeros(total_days) #Rt. This variable will be declared later

	S[0] = population_size - 1
	I[0] = 1
	max_infections = 1
	R[0] = 0

	time_run_start = time.time()
	#The days are in range [0,total_days-1]
	#In the worst case the pandemic ends at the end of the simulation
	end_epidemic = total_days-1
	for d in range(0,total_days-1):
		new_infected = 0
		new_recovered = 0
		if(debug):
			print(f'Day {d}, S={S[d]}, I={I[d]}, R={R[d]}, Total: {S[d]+I[d]+R[d]}',end='\n')
		# print(f'Day: {d}, Situation: S: {S[d]}, I: {I[d]}, R: {R[d]}, Total: {S[d]+I[d]+R[d]}')
		screen.fill((225, 225, 225))

		time_start_div_regions = time.time()
		#Dictionary with: 
		#		key: the number of the region
		#		value: a set with all the Susceptible individuals in that region
		susceptibles_per_regions = {}
		if(extension):
			#Create an entry in the dict for each region region
			for i in range(number_regions**2):
				susceptibles_per_regions[i] = set()

			#Loop over all the population
			for p in population:
				#Move the points randomly
				p.Move(length_movement)
				#Draw the Individual at its position
				p.PlotCircle(screen,screen_size)

				#Find the regions for Susceptible and Infected people
				if(p.category!='r'):
					#Get the belonging region
					region = ReturnRegion(p.pos)
					if(p.category=='s'):
						#Add it to the dict only if is a Susceptible
						susceptibles_per_regions[region].add(p.id)
					else:
						#Update the infected's region
						p.region = region
		else:
			for p in population:
				#In both cases (extension=True/False) draw the individuals in their positions
				#For the case extension=False, since there is no movement, it is still needed to update the color of the individuals
				#It is a fast computation anyway
				p.PlotCircle(screen,screen_size)

		#Update the screen
		pygame.display.flip()
		pygame.display.update()
		# time.sleep(5)

		time_end_div_regions = time.time()
		# print(f'Div in reg: {(time_end_div_regions-time_start_div_regions):.2f}', )
		#Variable used to store contacts in order to avoid double contacts (only for extension=False)
		contacts = set()
		num_infected = 0

		#Store a temponary variable since infected_individuals is changed during the loop
		current_infections = list(infected_individuals)
		#Loop over all the infected individual. m<N
		for inf_indi in current_infections:
			if(extension):
				#Get the region of the current infected individual
				infected_region = population[inf_indi].region
				#Get the list (of integers, the indeces) of the Susceptible pp in the infected_region
				population_in_region = susceptibles_per_regions[infected_region]
				# Loop over all the individuals in the infected_region

				for pop_index in population_in_region:
					#Calcaulate the distance between the two points: i and j
					#The parameter contact_distance is only needed for the case extension=True
					infected = population[inf_indi].CheckDistance(d,population[pop_index],contact_distance,transmission_rate,recovery_rate)

					if(infected):
						infected_individuals.add(pop_index)
						new_infected += 1

			else:
				#Choose a random number of people the infected ind will meet
				#Poisson distribution P(x,lambda), E(x) = lambda
				n_contacts = np.random.poisson(transmission_rate, size=1)
				new_infected_index = np.random.randint(population_size, size=n_contacts)

				c = 0
				for i in new_infected_index:
					#have been in contact with no one
					if(i not in contacts):
						if(population[i].category=='s'):
							infected_individuals.add(i)
							population[i].Infected(d,recovery_rate)
							#Update counter infections for the current infected individual
							population[inf_indi].daily_infections[d-population[inf_indi].day_infection-1]  += 1
							#Update statistic. Used for S,I,R variables
							new_infected+=1
					else:
						#Add to the contact list
						contacts.add(i)

				#Update counter infections for the current infected individual
				# population[inf_indi].daily_infections.append(c)

			#Plot the edge between the infected and all its contacts (Too many points!!!) 
			#population[inf_indi].PlotLink(screen,screen_size)
			
			#For each infected individual, evaluate if, on the next day, he has spent more than 'infection_period' days as infected -> he recovered
			#This returns the ID of the individual if he recovered otherwise nothing (None)
			recovered = population[inf_indi].UpdateState(d+1)
			if(recovered != None):
				infected_individuals.remove(recovered)
				new_recovered += 1

		# time.sleep(3)
		time_end_check_cont = time.time()
		if(debug):
			print(f'Infec T: {(time_end_check_cont-time_end_div_regions):.2f}, avg per inf: {((time_end_check_cont-time_end_div_regions)/(len(current_infections)+1) ):.4f}')

		#The future(tomorrow, d+1) states depends on:
		#the present states(today, d) and on the number of new infections and recovers(today, d)
		S[d+1] = S[d] - new_infected
		I[d+1] = I[d] + new_infected - new_recovered
		R[d+1] = R[d] + new_recovered

		# cum_infections = 0
		# n_infected = len(infected_individuals)
		# for i in infected_individuals:
		# 	cum_infections += population[i].infections
		# print(float(cum_infections),float(n_infected),float(cum_infections) / float(n_infected))
		# Rt[d+1] = float(cum_infections) / float(n_infected)

		# print(f'Situation: S: {S[d+1]}, I: {I[d+1]}, R: {R[d+1]}, Total: {S[d+1]+I[d+1]+R[d+1]}')
		if(I[d+1]<1):
			end_epidemic = d + 1
			break

		# time.sleep(5)
		time_end_day = time.time()
		if(debug):
			print(f'Total time: {(time_end_day-time_start_div_regions):.2f} \n')

	time_run_end = time.time()
	print(f'Run: {r},Total time: {(time_run_end-time_run_start):.2f}')
	print(f'Epidemic ended at day: {end_epidemic}')
	print(f'End situation: S: {S[end_epidemic]}, I: {I[end_epidemic]}, R: {R[end_epidemic]}')

	#Max number of infections and the day when this happens
	day_max_infections = np.argmax(I)
	max_infections = int(I[day_max_infections])
	print(f'Max Infections: {max_infections}, day at which occurs: {day_max_infections}')

	fig1, ax1 = plt.subplots(figsize=(12, 6), dpi=80)
	#The +1 since the right extreme is not included
	days = range(end_epidemic+1)
	S = S[:end_epidemic+1]
	I = I[:end_epidemic+1]
	R = R[:end_epidemic+1]

	ax1.plot(days,S, label='Susceptible')
	ax1.plot(days,I, label='Infected')
	ax1.plot(days,R, label='Recovered')

	title = 'Simulative SIR Model'	
	if(extension):
		title+=' (extension)'
	ax1.set_title(title)
	ax1.legend(loc='center right')
	ax1.set_xlabel('Days')
	ax1.set_ylabel('Number People')

	# plt.show()
	title = title.replace(' ','')
	save_title = (f'Images/{title}{r}')
	fig1.savefig(save_title)

	fig2, ax2 = plt.subplots(figsize=(12, 6), dpi=80)

	#Calculations Rt
	print('Calculation Rt....')
	Rt = np.zeros(end_epidemic+1)
	for d in range(end_epidemic-1):
		cum_contacts = 0
		distict_infected = set()
		for p in population:
			if(p.category=='r'):
				#c can be >=0 or False
				c = p.GetNumInfections(d)
				if(c>=0):
					cum_contacts += c
					distict_infected.add(p)
		print(d, cum_contacts,len(distict_infected))
		if(cum_contacts==0):
			break
		Rt[d] = cum_contacts/len(distict_infected)


	ax2.plot(days,Rt, label='Rt')
	title = 'Simulative SIR Model (Rt)'	
	if(extension):
		title+=' (extension)'
	ax2.set_title(title)
	ax2.legend(loc='center right')
	ax2.set_xlabel('Days')
	ax2.set_ylabel('Rt')

	# plt.show()
	title = title.replace(' ','')
	save_title = (f'Images/{title}{r}')
	fig2.savefig(save_title)

	print(f"{'#'*5}\tEnding Run: {r}\t{'#'*5}\n")

	# print(daily_infections)
	return max_infections, day_max_infections, end_epidemic

#SIMULATE
for r in range(n_runs):
	max_inf, max_day, end_epi = Simulator(r)

	#Check for not degenerate result
	if(max_day>20):
		# max_infections_runs[r] = max_inf
		# max_infections_day_runs[r] = max_day
		# epidemic_ends_runs[r] = end_epi
		max_infections_runs.append(max_inf)
		max_infections_day_runs.append(max_day)
		epidemic_ends_runs.append(end_epi)
	else:
		print('DEGENERATE ', r)

file_name = f"simulativeSIRmodel"
if(extension):
	file_name+='_ext'
simfile = open(file_name+'.dat', "w")
print("aveMaxInfec\tciMaxInfec\trel_errMaxInfec\taveMaxDayInfec\tciMaxDayInfec\trel_errMaxDayInfec\taveEndInfec\tciEndInfec\trel_errEndInfec",file=simfile)
aveMaxInfec, ciMaxInfec, rel_errMaxInfec = evaluate_conf_interval(max_infections_runs)
aveMaxDayInfec, ciMaxDayInfec, rel_errMaxDayInfec = evaluate_conf_interval(max_infections_day_runs)
aveEndInfec, ciEndInfec, rel_errEndInfec = evaluate_conf_interval(epidemic_ends_runs)

print(f"{aveMaxInfec}\t{ciMaxInfec}\t{rel_errMaxInfec}\t{aveMaxDayInfec}\t{ciMaxDayInfec}\t{rel_errMaxDayInfec}\t{aveEndInfec}\t{ciEndInfec}\t{rel_errEndInfec}",file=simfile)
print(f"maxInfections: {aveMaxInfec}\t{ciMaxInfec}\t{rel_errMaxInfec}")
print(f"maxDayInfections: {aveMaxDayInfec}\t{ciMaxDayInfec}\t{rel_errMaxDayInfec}")
print(f"epidemicEnd: {aveEndInfec}\t{ciEndInfec}\t{rel_errEndInfec}")

pygame.quit()