import simpy
import InteruptingAnotherProcess
from InteruptingAnotherProcess import InterruptingAnotherProcess

env = simpy.Environment()
car = InterruptingAnotherProcess.Car(env)
env.process(InterruptingAnotherProcess.driver(env, car))
env.run(until=15)