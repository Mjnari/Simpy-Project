import simpy
from numpy.random import RandomState


class Restaurant(object):
    def __init__(self, env, num_servers, serv_time):
        self.env = env
        self.server = simpy.Resource(env, num_servers)
        self.serv_time = serv_time

    def serve(self, env, customer_name, serve_time):
        yield self.env.timeout(serve_time)
        print('Finished serving %s at %.2f' % (customer_name, env.now))
        print('%d customers in line' % len(self.server.queue))


def customer(env, name, serve_time, restaurant):
    print('%s arrives at the restaurant at %.2f' % (name, env.now))
    with restaurant.server.request() as request:
        yield request

        print('%s starts receiving service at %.2f' % (name, env.now))
        yield env.process(restaurant.serve(env, name, serve_time))
        print('%s leaves the restaurant at %.2f' % (name, env.now))


def setup(env, num_servers, serve_time, lambda_arr_rate, prng=RandomState(0)):
    restaurant = Restaurant(env, num_servers, serve_time)
    interval_arrival_time = prng.exponential(1.0 / lambda_arr_rate)

    customer_count = 0

    # Create more customer arrivals while the simulation is running
    while True:
        yield env.timeout(interval_arrival_time)
        customer_count += 1
        env.process(customer(env, 'Customer %d' % customer_count, serve_time, restaurant))
