import simpy
import random
import Restaurant

DAYS = 365
# Sim time is in seconds by default
SIM_TIME = DAYS * 24 * 60 
RANDOM_SEED = 1

print('Restaurant')
random.seed(RANDOM_SEED)

env = simpy.Environment()
env.process(Restaurant.setup(env=env, num_servers=3, lambda_arr_rate=100, seed=RANDOM_SEED, days=DAYS))

env.run(until=SIM_TIME)
print('Simulation time complete. Simulation ran for %d days' % DAYS)
