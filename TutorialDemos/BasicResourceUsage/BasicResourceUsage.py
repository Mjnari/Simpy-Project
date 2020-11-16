# bcs = battery_charging_station
def car(env, name, bcs, driving_time, charge_duration):
    # drive to BCS
    yield env.timeout(driving_time)

    # Request a charging spot
    print('%s arriving at %d' % (name, env.now))
    with bcs.request() as req:
        yield req

        print('%s starting to charge at %s, charging duration %d' % (name, env.now, charge_duration))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %s' % (name, env.now))