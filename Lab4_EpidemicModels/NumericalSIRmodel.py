import numpy as np
import matplotlib.pyplot as plt

#How many people there are in the population_size
population_size = 10000
#Number of days we will consider
total_days = 365
#The number of people per day an infected person infects someone susceptible (beta) [day^-1]
transmission_rate=0.2
#The number of days an infencted person stays infected (gamma) [day^-1]
infection_period=14
recovery_rate=1/infection_period

print(f'Transmission Rate: {transmission_rate}')
print(f'Recovery Rate: {recovery_rate:.4f}')

initial_seed = 2500
np.random.seed(initial_seed)

S = np.zeros(total_days) #Susceptible
I = np.zeros(total_days) #Infected
R = np.zeros(total_days) #Recovered

#Initial conditions (day 0)
S[0] = population_size - 1
I[0] = 1
R[0] = 0

#The days are in range [0,total_days-1]
#In the worst case the pandemic ends at the end of the simulation
end_epidemic = total_days - 1
for d in range(0,total_days-1):
	# print(f'Day: {d}, Situation: S: {S[d]}, I: {I[d]}, R: {R[d]}, Total: {S[d]+I[d]+R[d]}')
	
	###	Solving Differential equations	###
	#The number of susceptible people tomorrow depends on today S and I values
	susceptible_today_value = (transmission_rate/population_size)*S[d]*I[d]
	infected_today_value = recovery_rate * I[d]
	# '1' is the delta time: 1 day in this case
	S[d+1] = S[d] - 1 * susceptible_today_value
	I[d+1] = I[d] + 1 * (susceptible_today_value-infected_today_value)
	R[d+1] = R[d] + 1 * infected_today_value
	if(I[d+1]<1):
		end_epidemic = d + 1
		break

print(f'Epidemic ended at day: {end_epidemic}')
print(f'End situation: S: {S[end_epidemic]:.2f}, I: {I[end_epidemic]:.2f}, R: {R[end_epidemic]:.2f}')


plt.figure(figsize=(12, 6), dpi=80)
#The +1 since the right extreme is not included
days = range(end_epidemic+1)
S = S[:end_epidemic+1]
I = I[:end_epidemic+1]
R = R[:end_epidemic+1]
plt.plot(days,S, label='Susceptible')
plt.plot(days,I, label='Infected')
plt.plot(days,R, label='Recovered')


title = 'Numerical SIR Model'	
plt.title(title)
plt.legend(loc='center right')
plt.xlabel('Days')
plt.ylabel('Number People')

remove_chars = [' ' , '=' , ',' , ':']
for r in remove_chars:
	title = title.replace(r,'')
save_title = (f'Images/{title}')
plt.savefig(save_title)

#Expected number of people the first infected individual will infect (Beta/gamma)
R0 = transmission_rate/recovery_rate
print(f'R0 value: {R0:.2f}')

#Max number of infections and the day when this happens
day_max_infections = np.argmax(I)
max_infections = int(I[day_max_infections])
print(f'Max Infections: {max_infections}, day at which occurs: {day_max_infections}')

plt.show()