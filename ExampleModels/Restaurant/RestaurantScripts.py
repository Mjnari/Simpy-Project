import simpy
import random
from ExampleModels.Restaurant import Restaurant

DAYS = 7
SIM_TIME = DAYS * 24 * 60 # sim time in minutes
RANDOM_SEED = 1

print('Restaurant')
random.seed(RANDOM_SEED)

env = simpy.Environment()
env.process(Restaurant.setup(env=env, num_servers=5, serve_time=1, lambda_arr_rate=10))

env.run(until=SIM_TIME)
print('Restaurant results after %s days' % DAYS)
