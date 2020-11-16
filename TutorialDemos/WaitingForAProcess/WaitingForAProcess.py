class Car(object):
    def __init__(self, env):
        self.env = env
        # Run everytime an instance is created
        self.action = env.process(self.run())

    def run(self):
        while True:
            print('Start parking and charging at %d' % self.env.now)
            charge_duration = 5
            # Yield the process returned by process()
            # In other words, waits for it to finish
            yield self.env.process(self.charge(charge_duration))

            # Charging has finished so now we can drive
            print('Start driving at %d' % self.env.now)
            trip_duration = 2
            yield self.env.timeout(trip_duration)

    def charge(self, duration):
        yield self.env.timeout(duration)