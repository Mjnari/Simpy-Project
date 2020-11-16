import simpy
from TutorialDemos import FirstProcess

env = simpy.Environment()
env.process(FirstProcess.car(env))
env.run(until=15)