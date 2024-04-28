import simpy
from ecs_sim.simulators import EVChargingStationAlpha

def main():
    
    env = simpy.Environment()
    
    num_timestamp = 10
    
    num_evse = 3
    lambda_poisson = 0.2
    max_charging_rate = 10
    
    
    ecs = EVChargingStationAlpha(env, num_evse, lambda_poisson, max_charging_rate)
    
    
    while env.peek() < num_timestamp:
        env.step()


if __name__ == '__main__':
    main()