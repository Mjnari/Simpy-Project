import simpy
from TutorialDemos.BasicResourceUsage import BasicResourceUsage

env = simpy.Environment()
bcs = simpy.Resource(env, capacity=2)

for i in range(4):
    env.process(BasicResourceUsage.car(env, 'Car %d' % i, bcs, i*2, 5))

env.run()