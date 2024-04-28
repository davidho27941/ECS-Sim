import simpy
import random
import numpy as np

from abc import abstractmethod, ABC
from collections import deque

from scipy.stats import truncnorm


class BaseEVChargingStation(ABC):
    def __init__(self, env, num_evse) -> None:
        self.env = env
        self.num_slot = 96
        self.num_evse = num_evse

    @abstractmethod
    def charge(self, car_id, energy_demand, arrivial_time):
        raise NotImplementedError(
            "A child class of `BaseEVChargingStation` must has a `charge` method implemented."
        )

    @abstractmethod
    def get_current_record(self):
        raise NotImplementedError(
            "A child class of `BaseEVChargingStation` must has a `get_current_record` method implemented."
        )

    @abstractmethod
    def arrive(self):
        raise NotImplementedError(
            "A child class of `BaseEVChargingStation` must has a `get_current_record` method implemented."
        )


class EVChargingStationAlpha(BaseEVChargingStation):
    def __init__(self, env, num_evse, lambda_poisson, max_charging_rate) -> None:
        super().__init__(env, num_evse)

        self.lambda_poisson = lambda_poisson

        self.evse = simpy.Resource(env, capacity=num_evse)
        self.backend_proc = env.process(self.arrive())

        self.max_charging_rate = max_charging_rate
        self.charged_history = {
            f"evse_{idx}": deque(maxlen=self.num_slot) for idx in range(self.num_evse)
        }
        self.vehicles = {}

    def generate_customer(self):
        patience = np.random.randint(1,3)
        energy_demand = truncnorm.rvs(2, 50, loc=25)

        return patience, energy_demand

    def charge(self, car_id, energy_demand, arrivial_time, patience):
        with self.evse.request() as req:

            results = yield req | self.env.timeout(patience)

            if req in results:
                evse_id = self.find_free_charger()

                self.vehicles[evse_id] = {
                    "required_energy": energy_demand,
                    "accumulated_energy": 0,
                }

                wait_duration = self.env.now - arrivial_time
                print(
                    f"EV {car_id} start charging at {self.env.now}. Waiting Time: {wait_duration}"
                )

                while (
                    self.vehicles[evse_id]["accumulated_energy"]
                    < self.vehicles[evse_id]["required_energy"]
                ):

                    available_energy = (
                        self.max_charging_rate / self.get_allocated_evse_number()
                    )
                    self.vehicles[evse_id]["accumulated_energy"] += available_energy

                    self.charged_history[f"evse_{evse_id}"].append(available_energy)

                    print(
                        f"EV {car_id} received {available_energy} kWh at {self.env.now}"
                    )

                    yield self.env.timeout(1)

                del self.vehicles[evse_id]

                print(f"EV {car_id} leave at {self.env.now}")

            else:
                print(
                    f"+EV {car_id} leave without charged due to waiting too long.\n"
                    f"+Patience: {patience}. Current time: {self.env.now}"
                )
                yield self.env.timeout(1)

    def get_current_record(self):
        tmp_history = []
        for evse_id in range(self.num_evse):
            tmp_deque2list = list(self.charged_history[f'evse_{evse_id}'])
            tmp_history.append(tmp_deque2list)
        return tmp_history

    def get_allocated_evse_number(self):
        return len(self.vehicles)

    def find_free_charger(self):
        for evse_id in range(self.num_evse):
            if evse_id not in self.vehicles:
                return evse_id
        raise Exception("All EVSE are in use.")
    
    # def fill_zero_watch_dog(self):
    #     print(self.env.active_process)
        
    #     for evse_id in range(self.num_evse):
    #         if evse_id not in self.vehicles:
    #             self.charged_history[f'evse_{evse_id}'].append(0.0)
    #     yield self.env.timeout(0)
        
    # def watch_dog(self):
    #     print("-"*80)
    #     print(f"{self.env.now=}")
    #     print(self.env.active_process)
    #     for evse_id in range(self.num_evse):
    #         history = self.charged_history[f'evse_{evse_id}']
    #         print(f"{evse_id=}, {len(history)=}, {history=}")
    #     yield self.env.timeout(0)
    #     print("-"*80)
        

    def arrive(self):
        car_id = 0
        while True:
            if np.random.random() < self.lambda_poisson:
                patience, energy_demand = self.generate_customer()
                arrival_time = self.env.now

                print(f"EV {car_id} arrived at {arrival_time}.")
                print(f"EV {car_id} require {energy_demand} kWh.")

                self.env.process(
                    self.charge(
                        car_id,
                        energy_demand,
                        arrival_time,
                        patience,
                    )
                )
                car_id += 1
            else:
                yield self.env.timeout(1)
            
            # yield self.env.process(self.fill_zero_watch_dog())
            # yield self.env.process(self.watch_dog())
            