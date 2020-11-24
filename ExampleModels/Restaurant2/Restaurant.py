import simpy
from numpy.random import RandomState


class Restaurant(object):
    def __init__(self, env, num_servers):
        self.env = env
        self.is_open = True
        self.line_length = 0
        self.max_line_length = 0
        self.customer_leave_count = 0
        # Servers are resources, similar to Arena
        self.server = simpy.Resource(env, num_servers)
        # Time the restaurant is open
        self.open_period = 15 * 60
        self.closed_period = 24 * 60 - self.open_period
        self.env.process(self.handle_is_open())

    # Process for serving the customer
    def serve(self, env, customer_name, serve_time):
        yield self.env.timeout(serve_time)
        print('Finished serving %s at %.2f' % (customer_name, env.now))
        print('%d customers in line' % self.line_length)

    def handle_is_open(self):
        while True:
            if self.is_open:
                print('Restuarant is open!')
                yield self.env.timeout(self.open_period)
                self.is_open = False
            else:
                # End of business hours, so empty the line
                # But finish serving those already being served
                print('Closing for the night')
                if self.line_length > self.max_line_length:
                    self.max_line_length = self.line_length
                self.line_length = 0
                yield self.env.timeout(self.closed_period)
                self.is_open = True

                # self.analysis()

    # def analysis(self):
        # print('%d customers were served, averaging %d per day' % (customer_count, customer_count / days))
        # print('The longest the line got was %d customers long' % restaurant.max_line_length)
        # print('%d customers got impatient and left' % restaurant.customer_leave_count)

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

    # Simulates the customer arriving and being processed
    def simulate(self):
        print('%s arrives at the restaurant at %.2f' % (self.name, self.env.now))
        self.restaurant.line_length += 1
        # This with statement handles the following:
        # When a server resource is available, use it
        # When the server resource is done being used, release it
        # Without the with statement I would have to manually seize and release resources
        with self.restaurant.server.request() as request:
            # Either wait until a server is free to serve this customer
            # or until this customer runs out of patience and leaves the line
            results = yield request | self.env.timeout(self.patience)
            wait = self.env.now - self.arrival_time

            if self.restaurant.is_open:
                # Restarant is open and customer still has patience, so start serving customer
                if request in results:
                    print('%s starts receiving service at %.2f' % (self.name, self.env.now))
                    print('%s waited %.2f seconds in line' % (self.name, wait))
                    # Serve the customer
                    yield self.env.process(self.restaurant.serve(self.env, self.name, self.serve_time))
                    print('%s leaves the restaurant at %.2f' % (self.name, self.env.now))
                # Restarant is open but the customer has run out of patience in line, the customer leaves
                else:
                    print('%s got tired of waiting in line after %.2f seconds, so they left' % (self.name, wait))
                    self.restaurant.customer_leave_count += 1
            # Restaurant is closed. Those currently being served will finish being served
            # Those in line will be sent away
            else:
                print('%s left since they were still in line when the restaurant closed' % self.name)


def setup(env, num_servers, lambda_arr_rate, seed, days):
    restaurant = Restaurant(env, num_servers)
    # The interval arrival time for when customers arive at the restuarant
    # This is a Poisson(lambda) distribution
    interval_arrival_time = RandomState(seed).poisson(lambda_arr_rate)

    customer_count = 0

    # Create more customer arrivals, and process them
    # while the simulation is running
    while True:
        yield env.timeout(interval_arrival_time)
        if (restaurant.is_open):
            # A customer arrives at the end of this timeout, so
            # a new customer object is created
            customer_count += 1
            customer = Customer(env, customer_count, restaurant, seed)
            # Process that customer object
            env.process(customer.simulate())
        else:
            yield env.timeout(restaurant.closed_period)
