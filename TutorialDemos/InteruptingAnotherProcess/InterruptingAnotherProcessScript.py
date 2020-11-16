import simpy
from TutorialDemos.InteruptingAnotherProcess import InterruptingAnotherProcess

env = simpy.Environment()
car = InterruptingAnotherProcess.Car(env)
env.process(InterruptingAnotherProcess.driver(env, car))
env.run(until=15)