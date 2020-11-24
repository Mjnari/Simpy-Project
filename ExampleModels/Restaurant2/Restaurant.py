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
    def __init__(self, env, name, restaurant):
        self.env = env
        self.name = name
        self.restaurant = restaurant
        self.serve_time = 1

    def handle(self):
        print('%s arrives at the restaurant at %.2f' % (self.name, self.env.now))
        with self.restaurant.server.request() as request:
            yield request

            print('%s starts receiving service at %.2f' % (self.name, self.env.now))
            yield self.env.process(self.restaurant.serve(self.env, self.name, self.serve_time))
            print('%s leaves the restaurant at %.2f' % (self.name, self.env.now))

# def customer(env, name, restaurant):
#     print('%s arrives at the restaurant at %.2f' % (name, env.now))
#     with restaurant.server.request() as request:
#         yield request

#         print('%s starts receiving service at %.2f' % (name, env.now))
#         serve_time = 1
#         yield env.process(restaurant.serve(env, name, serve_time))
#         print('%s leaves the restaurant at %.2f' % (name, env.now))


def setup(env, num_servers, lambda_arr_rate, seed):
    restaurant = Restaurant(env, num_servers)
    interval_arrival_time = RandomState(seed).exponential(1.0 / lambda_arr_rate)

    customer_count = 0

    # Create more customer arrivals while the simulation is running
    while True:
        yield env.timeout(interval_arrival_time)
        customer_count += 1
        customer = Customer(env, 'Customer %d' % customer_count, restaurant)
        env.process(customer.handle())
