import numpy as np
import matplotlib.pyplot as plt
import pygame
import time

class Individual():
	def __init__(self):
		#Cordinates (x and y) of the position
		self.pos = np.random.uniform(size=2)
		#Categories: 0:, 1:
		self.category=0
		#Number of days since the infection day
		self.day_infection = 0
		#List of all contacts. These are integers for optimization purposes
		self.contacts = []

	#Update the category with a given one
	def UpdateState(self,cat):
		self.category=cat
	#Check if an Individual is within a range distance
	def CheckDistance(self,other,distance):
		other_pos = other.pos
		#First check distance
		if(math.abs(self.pos[0]-other_pos[0])<=distance and math.abs(self.pos[1]-other_pos[1])<=distance):
			#Calculate the distance between the 2 points. Avoid calculate the sqrt
			dis = (self.pos[0]-other_pos[0])**2 + (self.pos[1]-other_pos[1])**2
			if(dis<=distance**2):
				#Withing the range (Contact)
				self.PlotLink(screen,other_pos)
				return True
		#Too far (no contacts)
		return False
	#Update contacts, all Individuals within a distance range
	def UpdateContacts(self,contacts):
		self.contacts=contacts
	#Returns a list of integers of infected Individuals
	def Infections(self,beta):
		infected = []
		for c in contacts:
			#The contact individual is susceptible to infection
			if(c.category==0):
				#Flip a 'coin' to infect the contact
				r = np.random()
				if(r<beta):
					Infected.append(c)
		return Infected
	#Move the Individual to a new random position
	def Move(self):
		range = 0.1
		direction = np.random.uniform(-range,range,2)
		self.pos+=direction
		#Outside the box
		if( ((self.pos[0]>0 or self.pos[0]<1) and (self.pos[1]>0 or self.pos[1]<1))  is False ):
			#Move towards the center
			direction = (0.5,0.5) - self.pos
			self.pos += np.random.uniform(size=2) * direction
	#Plot the Individual shape: a circle
	def PlotCircle(self,screen,screen_size):
		print(self.pos)
		if(self.category==0):
			color = (0,1,1) #Susceptible: (0,0,0)
		elif(self.category==1):
			color = (1,0,0) #Infected: (0,0,0)
		elif(self.category==2):
			color = (0,0,1) #Recovered: (0,0,0)
		pygame.draw.circle(screen, color, self.pos*screen_size, 5)
	#Draw a line between this point and a destination point. One line for each contact
	def PlotLink(self,screen,dest_pos,screen_size):
		pygame.draw.line(screen, (0,0,0), self.pos*screen_size, dest_pos*screen_size)

pygame.init()
screen_size = [800, 600]
screen = pygame.display.set_mode(screen_size)

#How many people there are in the population
population_size = 10 # N
#Number of days we will consider
total_days = 5
#The number of people per day an infected person infects someone susceptible (beta) [day^-1]
transmission_rate=0.2
#The number of days an infencted person stays infeccted (gamma) [day^-1]
infection_period=14
recovery_rate=1/infection_period

print('Transmission Rate: ', transmission_rate)
print('Recovery Rate: ', recovery_rate)

initial_seed = 2500
np.random.seed(initial_seed)

#Individuals
population = [Individual() for i in range(population_size)]
#List with all infected people indeces. This is used for optimization purposes
infected_individuals = set()

#Initial conditions (day 0)
first_infected = np.random.randint(population_size)
population[first_infected].UpdateState(1)
infected_individuals.add(first_infected)

end_epidemic = np.Inf
running = True

screen.fill((255, 255, 255))
#Skip the day 0
for d in range(1,total_days):

	#Loop over all the population
	for pop_index in range(population_size):
		#Draw the Individual at its position
		population[pop_index].PlotCircle(screen,screen_size)

		# #Loop over all the infected individual. m<N
		# for inf_indi in infected_individuals:
		# contacts = []
		# 	if(inf_indi is not pop_index):
		# 		#Calcaulate the distance between the two points: i and j
		# 		close = population[inf_indi].CheckDistance(population[pop_index],1)
		# 		if(close):
		# 			contacts.append(inf_indi)
		# #Update the Individual's concact list
		# population[inf_indi].UpdateContacts(contacts)
		# #New infections. Subset of all the conflicts 
		# infections = population[inf_indi].Infections(beta)
		# #Add new infections to the infection set
		# for ii in infections:
		# 	infected_individuals.add(ii)

	for i in population:
		#Move the points for the next day
		i.Move()
	print(d)
	pygame.display.flip()
	time.sleep(5)


pygame.quit()

'''
S = np.zeros(total_days) #Susceptible
I = np.zeros(total_days) #Infected
R = np.zeros(total_days) #Recovered

#Initial conditions (day 0)
S[0] = population_size - 1
I[0] = 1
R[0] = 0

end_epidemic = np.Inf
#Skip the day 0
for d in range(1,365):
	###	Solving Differential equations	###
	#The number of susceptible people tomorrow depends on today S and I values
	susceptible_today_value = (transmission_rate/population_size)*S[d-1]*I[d-1]
	infected_today_value = recovery_rate * I[d-1]
	# '1' is the delta time: 1 day in this case
	S[d] = S[d-1] - 1 * susceptible_today_value
	I[d] = I[d-1] + 1 * (susceptible_today_value-infected_today_value)
	R[d] = R[d-1] + 1 * infected_today_value
	if(I[d]<1):
		end_epidemic = d
		break

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
'''