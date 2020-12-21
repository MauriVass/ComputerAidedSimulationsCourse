import numpy as np
import matplotlib.pyplot as plt
import pygame

class Individual():
	def __init__(self):
		#Cordinates (x and y) of the position
		self.pos = np.zeros(2)
		#Categories: 0:, 1:
		self.category=0
		#List of all contacts. These are integers for optimization purposes
		self.contacts = []
	#
	def UpdateState(self,cat):
		self.category=0
	#Find all Individual within a distance range
	def AddContacts(self,contacts):
		self.contacts=contacts
	#Returns a list of integers of infected Individuals
	def Infections(self):
		infected = []
		return Infected
	#Move the Individual to a new random position
	def Move(self,boundaries):
		return
	#Plot the Individual shape: a circle
	def PlotCircle(self,screen):
		color = (0,0,0)
		pygame.draw.circle(screen, color, self.pos, 5)
	#Draw a line between this point and a destination point. One line for each contact
	def PlotLink(self,screen,dest_pos):
		pygame.draw.line(screen, color, self.pos, dest_pos)

l = [Individual() for i in range(10)]


'''
#How many people there are in the population
population = 10000
#Number of days we will consider
total_days = 365
#The number of people per day an infected person infects someone susceptible (beta) [day^-1]
transmission_rate=0.2
#The number of days an infencted person stays infeccted (gamma) [day^-1]
infection_period=14
recovery_rate=1/infection_period

print('Transmission Rate: ', transmission_rate)
print('Recovery Rate: ', recovery_rate)

initial_seed = 2500
np.random.seed(initial_seed)

S = np.zeros(total_days) #Susceptible
I = np.zeros(total_days) #Infected
R = np.zeros(total_days) #Recovered

#Initial conditions (day 0)
S[0] = population - 1
I[0] = 1
R[0] = 0

end_epidemic = np.Inf
#Skip the day 0
for d in range(1,365):
	###	Solving Differential equations	###
	#The number of susceptible people tomorrow depends on today S and I values
	susceptible_today_value = (transmission_rate/population)*S[d-1]*I[d-1]
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