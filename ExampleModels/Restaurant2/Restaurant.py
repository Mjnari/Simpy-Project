import simpy
from numpy.random import RandomState


class Restaurant(object):
    def __init__(self, env, num_servers):
        self.env = env
        # Servers are resources, similar to Arena
        self.server = simpy.Resource(env, num_servers)

    # Process for serving the customer
    def serve(self, env, customer_name, serve_time):
        yield self.env.timeout(serve_time)
        print('Finished serving %s at %.2f' % (customer_name, env.now))
        print('%d customers in line' % len(self.server.queue))

class Customer(object):
    def __init__(self, env, customer_count, restaurant, seed):
        self.env = env
        self.name = 'Customer ' + str(customer_count)
        self.customer_count = customer_count
        self.restaurant = restaurant
        self.arrival_time = env.now
        # The amount of time this customer is willing to wait in line
        self.patience = self.get_patience(seed)
        # The amount of time this customer spends ordering + eating
        self.serve_time = self.get_serve_time(seed)

    # Calculates serve time as Nor(3000, 600) seconds
    # If this number is <= 0 then re-run it
    def get_serve_time(self, seed):
        serve_time = RandomState(seed + self.customer_count).normal(3000, 600)
        while serve_time <= 0:
            serve_time = RandomState(seed + self.customer_count).normal(3000, 600)
        return serve_time

    # Calculates patiences as exp(6000) seconds
    def get_patience(self, seed):
        return RandomState(seed + self.customer_count).exponential(6000)

    def handle(self):
        print('%s arrives at the restaurant at %.2f' % (self.name, self.env.now))
        # This with statement handles the following:
        # When a server resource is available, use it
        # When the server resource is done being used, release it
        # Without the with statement I would have to manually seize and release resources
        with self.restaurant.server.request() as request:
            # Either wait until a server is free to serve this customer
            # or until this customer runs out of patience and leaves the line
            results = yield request | self.env.timeout(self.patience)
            wait = self.env.now - self.arrival_time

            if request in results:
                print('%s starts receiving service at %.2f' % (self.name, self.env.now))
                print('%s waited %d seconds in line' % (self.name, wait))
                # Serve the customer
                yield self.env.process(self.restaurant.serve(self.env, self.name, self.serve_time))
                print('%s leaves the restaurant at %.2f' % (self.name, self.env.now))
            else:
                print('%s got tired of waiting in line after %d seconds, so they left' % (self.name, wait))


def setup(env, num_servers, lambda_arr_rate, seed):
    restaurant = Restaurant(env, num_servers)
    # The interval arrival time for when customers arive at the restuarant
    # This is a Poisson(lambda) distribution
    interval_arrival_time = RandomState(seed).poisson(lambda_arr_rate)

    customer_count = 0

    # Create more customer arrivals, and process them
    # while the simulation is running
    while True:
        # A customer arrives at the end of this timeout, so
        # a new customer object is created
        yield env.timeout(interval_arrival_time)
        customer_count += 1
        customer = Customer(env, customer_count, restaurant, seed)
        # Process that customer object
        env.process(customer.handle())
