import simpy
from TutorialDemos import WaitingForAProcess

env = simpy.Environment()
car = WaitingForAProcess.Car(env)
env.run(until=15)