import simpy
from numpy.random import RandomState


class Restaurant(object):
    def __init__(self, env, num_servers):
        self.env = env
        self.is_open = True
        # Servers are resources, similar to Arena
        self.server = simpy.Resource(env, num_servers)
        # Time the restaurant is open
        self.open_period = 15 * 60
        self.closed_period = 24 * 60 - self.open_period
        self.env.process(self.handle_is_open())
        # Values used just for the analysis
        self.stats = {
            "day": 1,
            "line_length": 0,
            "server_count": num_servers,
            "served_today": 0,
            "served_total": 0,
            "max_line_today": 0,
            "max_line_total": 0,
            "customer_leave_today": 0,
            "customer_leave_total": 0
        }

    # Process for serving the customer
    def serve(self, env, customer_name, serve_time):
        yield self.env.timeout(serve_time)
        print('Finished serving %s at %.2f' % (customer_name, env.now))
        print('%d customers in line' % self.stats["line_length"])

        self.stats["served_today"] += 1
        self.stats["served_total"] += 1

    def handle_is_open(self):
        while True:
            if self.is_open:
                print('\nRestuarant is open!')
                yield self.env.timeout(self.open_period)
                self.is_open = False
            else:
                # End of business hours, so empty the line but
                # finish serving those already being served.
                # Code to handle emptying the line is in Customer.simulate()
                print('Closing for the night. Successful day number %d!' % self.stats["day"])
                self.stats["day"] += 1
                
                # Printing and maintaining some stats
                self.update_line_length_stats()
                self.analysis()
                self.reset_stats()

                yield self.env.timeout(self.closed_period)
                self.is_open = True

    # Print end of day stats
    def analysis(self):
        print('\nStats for today:')
        print('%d customers served today' % self.stats["served_today"])
        print('The longest the line got today was %d customers long' % self.stats["max_line_today"])
        print('%d customers got impatient and left today' % self.stats["customer_leave_today"])
        print('%.2f average customers served per server today' % (self.stats["served_today"]/self.stats["server_count"]))

        print('\nOverall stats:')
        print('%d customers served in total, averaging %.2f per day' % (self.stats["served_total"], self.stats["served_total"]/self.stats["day"]))
        print('The longest the line has ever been is %d customers long' % self.stats["max_line_total"])
        print('%d customers have gotten impatient and left in total' % self.stats["customer_leave_total"])
        print('%.2f average customers served per server, per day\n' % (self.stats["served_total"]/self.stats["server_count"]/self.stats["day"]))

    # Maintanance for some of the stats printed by analysis()
    def reset_stats(self):
        self.stats["line_length"] = 0
        self.stats["served_today"] = 0
        self.stats["max_line_today"] = 0
        self.stats["customer_leave_today"] = 0

    # Maintanance for some of the stats printed by analysis()
    def update_line_length_stats(self):
        if self.stats["line_length"] > self.stats["max_line_total"]:
            self.stats["max_line_total"] = self.stats["line_length"]
        if self.stats["line_length"] > self.stats["max_line_today"]:
            self.stats["max_line_today"] = self.stats["line_length"]

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

    # Calculates serve time as Nor(60, 15) minutes
    # If this number is <= 0 then re-run it
    # This means this is not truely a normal distribution, it also makes it vulnerable to
    # significantly slowing the run time if numbers are chose poorly
    # Also can cause sequences of customers with the same serve times
    def get_serve_time(self, seed):
        buffer = 0
        serve_time = RandomState(seed + self.customer_count).normal(60, 15)
        while serve_time <= 0:
            buffer += 1
            serve_time = RandomState(seed + self.customer_count + buffer).normal(60, 15)
        return serve_time

    # Calculates patiences as exp(60) minutes
    def get_patience(self, seed):
        return RandomState(seed + self.customer_count).exponential(60)

    # Simulates the customer arriving and being processed
    def simulate(self):
        print('%s arrives at the restaurant at %.2f' % (self.name, self.env.now))
        self.restaurant.stats["line_length"] += 1
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
                # Remove customer from line  
                self.restaurant.stats["line_length"] -= 1
                # Restarant is open and customer still has patience, so start serving customer
                if request in results:
                    print('%s starts receiving service at %.2f' % (self.name, self.env.now))
                    print('%s waited %.2f minutes in line' % (self.name, wait))
                    # Serve the customer
                    yield self.env.process(self.restaurant.serve(self.env, self.name, self.serve_time))
                    print('%s leaves the restaurant at %.2f' % (self.name, self.env.now))
                # Restarant is open but the customer has run out of patience in line, the customer leaves
                else:
                    print('%s got tired of waiting in line for %.2f minutes, so they left' % (self.name, wait))
                    self.restaurant.stats["customer_leave_today"] += 1
                    self.restaurant.stats["customer_leave_total"] += 1
            # Restaurant is closed. Those currently being served will finish being served
            # Those in line will be sent away
            else:
                print('%s left since they were still in line when the restaurant closed' % self.name)


def setup(env, num_servers, lambda_arr_rate, seed, days):
    restaurant = Restaurant(env, num_servers)

    buffer = 0
    customer_count = 0

    # Create more customer arrivals, and process them
    # while the simulation is running
    while True:
        # The interval arrival time for when customers arive at the restuarant
        # This is a Poisson(lambda) distribution
        interval_arrival_time = RandomState(seed + buffer).poisson(lambda_arr_rate)
        buffer += 1
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
