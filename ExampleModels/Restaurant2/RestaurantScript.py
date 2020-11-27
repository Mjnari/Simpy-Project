import simpy
import random
import Restaurant

DAYS = 365
# Sim time is arbitrary, but most examples have it in minutes by default
SIM_TIME = DAYS * 24 * 60 
RANDOM_SEED = 1

print('Restaurant')
random.seed(RANDOM_SEED)

env = simpy.Environment()
env.process(Restaurant.setup(env=env, num_servers=8, lambda_arr_rate=4, seed=RANDOM_SEED, days=DAYS))

env.run(until=SIM_TIME)
print('Simulation time complete. Simulation ran for %d days' % DAYS)
