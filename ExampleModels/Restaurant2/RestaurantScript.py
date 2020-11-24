import simpy
import random
import Restaurant

DAYS = 2
SIM_TIME = DAYS * 24 * 60 # sim time in minutes
RANDOM_SEED = 1

print('Restaurant')
random.seed(RANDOM_SEED)

env = simpy.Environment()
env.process(Restaurant.setup(env=env, num_servers=5, lambda_arr_rate=10, seed=RANDOM_SEED))

env.run(until=SIM_TIME)
print('Restaurant results after %s days' % DAYS)
