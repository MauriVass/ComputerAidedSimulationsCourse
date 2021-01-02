import numpy as np
import matplotlib.pyplot as plt
import pygame
import time
from scipy import spatial

class Individual():
	def __init__(self,id):
		#Individual ID
		self.id = id
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
			s = 6
		elif(self.category==2):
			color = (0,255,100) #Recovered
		pygame.draw.circle(screen, color, ((0.1,0.1)+self.pos)*screen_size, s)

	#Draw a line between this point and a destination point. One line for each contact
	def PlotLink(self,screen,screen_size):
		for c in self.contacts:
			pygame.draw.line(screen, (0,0,0), self.pos*screen_size, c.pos*screen_size)

pygame.init()
screen_size = [800, 600]
screen = pygame.display.set_mode(screen_size)

#How many people there are in the population
population_size = 2000 # N
#Number of days we will consider
total_days = 365
#The number of people per day an infected person infects someone susceptible (beta) [day^-1]
transmission_rate=0.2
#The number of days an infencted person stays infeccted (gamma) [day^-1]
infection_period=14
recovery_rate=1/infection_period

#How many
number_sections = 9

print('Transmission Rate: ', transmission_rate)
print('Recovery Rate: ', recovery_rate)

initial_seed = 2501
np.random.seed(initial_seed)

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
screen_size = [700, 500]
tt_init = time.time()
#Skip the day 0
for d in range(1,total_days):
	new_infected = 0
	new_recovered = 0
	print('Day ',d)
	ti = time.time()
	screen.fill((255, 255, 255))

	#Loop over all the population
	for p in population:
		#Draw the Individual at its position
		p.PlotCircle(screen,screen_size)
	te_plot = time.time()
	# print(f'Plotting Time: {(te_plot-ti):.2f}')

	current_infections = list(infected_individuals)
	#Loop over all the infected individual. m<N
	for inf_indi in current_infections:
		if(True):
			# Loop over all the population
			for pop_index in range(population_size):
				if(inf_indi is not pop_index):
					#Calcaulate the distance between the two points: i and j
					ii = population[inf_indi].CheckDistance(population[pop_index],.01)
					if(ii):
						infected_individuals.add(pop_index)
						new_infected += 1
		#Plot the edge between the infected and all its contacts		
		#population[inf_indi].PlotLink(screen,screen_size)
		else:
			points = [population[x].pos for x in range(population_size)]
			tree = spatial.KDTree(points)
			contacts = []
			contacts = tree.query_ball_point(population[inf_indi].pos, 0.01)
			population[inf_indi].contacts = [population[x] for x in contacts]
		
		recovered = population[inf_indi].UpdateState(infection_period=infection_period)
		if(recovered != None):
			infected_individuals.remove(recovered)
			new_recovered += 1
			# print(f'Recovered: {recovered}, day: {d} ##################################')

		if(False):
			for inf_indi in current_infections:
				#Update the Individual's concact list
				#population[inf_indi].UpdateContacts(contacts)
				#New infections. Subset of all the conflicts 
				infections = population[inf_indi].Infections(transmission_rate)
				if(False):
					infections = []
					contacts = population[inf_indi].contacts
					for c in contacts:
						ind = population[c]
						#The contact individual is susceptible to infection
						#print(c.category)
						if(ind.category == 0):
							#Flip a 'coin' to infect the contact
							r = np.random.uniform()
							#print(r)
							if(r<transmission_rate):
								infections.append(ind.id)
								ind.UpdateState(1)
				#print(f'New Infections: {len(infections)}')
				#Add new infections to the infection set
				for ii in infections:
					infected_individuals.add(ii)
	te = time.time()
	print(f'Checking Distance Time: {(te-te_plot):.2f}')

	for p in population:
		#Move the points for the next day
		p.Move(0.15)

	S[d] = S[d-1] - new_infected
	I[d] = I[d-1] + new_infected - new_recovered
	R[d] = R[d-1] + new_recovered

	print(f'Situation: S: {S[d]}, I: {I[d]}, R: {R[d]}, Total: {S[d]+I[d]+R[d]}')
	if(I[d]<1):
		end_epidemic = d
		break

	pygame.display.flip()
	pygame.display.update()
	time.sleep(.01)

tt_end = time.time()
print(f'Total time: {(tt_end-tt_init):.2f}')
pygame.quit()

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

plt.show()