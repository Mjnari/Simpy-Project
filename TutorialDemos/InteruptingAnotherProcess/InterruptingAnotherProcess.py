import simpy


def driver(env, car):
    yield env.timeout(3)
    car.action.interrupt()


class Car(object):
    def __init__(self, env):
        self.env = env
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('Start parking and charging at %d' % self.env.now)
            charge_duration = 5
            print('Supposed to charge for %d seconds' % charge_duration)
            # We may get interrupted while charging the battery
            try:
                yield self.env.process(self.charge(charge_duration))
            except simpy.Interrupt:
                # On interrupt, stop charging and switch
                # to the driving state
                print('Was interrupted. Hope the batter is charged enough!')

            print('Start driving at %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        yield self.env.timeout(duration)
