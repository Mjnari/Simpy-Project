import simpy
from numpy.random import RandomState


class Restaurant(object):
    def __init__(self, env, num_servers):
        self.env = env
        self.server = simpy.Resource(env, num_servers)

    def serve(self, env, customer_name, serve_time):
        yield self.env.timeout(serve_time)
        print('Finished serving %s at %.2f' % (customer_name, env.now))
        print('%d customers in line' % len(self.server.queue))

class Customer(object):
    def __init__(self, env, name, restaurant, seed):
        self.env = env
        self.name = name
        self.restaurant = restaurant
        self.serve_time = self.get_serve_time(seed)
        self.patience = self.get_patience(seed)

    def get_serve_time(self, seed):
        serve_time = RandomState(seed).normal(3000, 600)
        while serve_time <= 0:
            serve_time = RandomState(seed).normal(3000, 600)
        return serve_time

    def get_patience(self, seed):
        return RandomState(seed).exponential(6000)

    def handle(self):
        print('%s arrives at the restaurant at %.2f' % (self.name, self.env.now))
        with self.restaurant.server.request() as request:
            results = yield request | self.env.timeout(self.patience)

            if request in results:
                print('%s starts receiving service at %.2f' % (self.name, self.env.now))
                yield self.env.process(self.restaurant.serve(self.env, self.name, self.serve_time))
                print('%s leaves the restaurant at %.2f' % (self.name, self.env.now))
            else:
                print('%s got tired of waiting in line and left' % self.name)


def setup(env, num_servers, lambda_arr_rate, seed):
    restaurant = Restaurant(env, num_servers)
    interval_arrival_time = RandomState(seed).exponential(1.0 / lambda_arr_rate)

    customer_count = 0

    # Create more customer arrivals while the simulation is running
    while True:
        yield env.timeout(interval_arrival_time)
        customer_count += 1
        customer = Customer(env, 'Customer %d' % customer_count, restaurant, seed)
        env.process(customer.handle())
