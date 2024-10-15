import pandas

from use_cases.swim.swim_client import SwimClient
from use_cases.adaptation_logic import AdaptationLogic
from models.feature_model import NumericalFM
from models.cmab import CMAB
from use_cases.adaptation_logic import SimulatorInterface

import time


class SWIMSimulatorInterface(SimulatorInterface):

    def __init__(self, feature_model: NumericalFM) -> None:
        super().__init__(feature_model)
        self.swim_client = SwimClient()

        self.servers = None
        self.dimmer = None

    def sensor_interface(self) -> tuple[pandas.Series, float]:

        arrival_rate = self.swim_client.get_arrival_rate()
        if arrival_rate == None:
            raise ValueError("Simulator not connected?")

        servers = self.swim_client.get_servers()
        self.servers = servers
        dimmer = self.swim_client.get_dimmer()
        self.dimmer = dimmer

        arrival_rate_feature = (
            self.feature_model.numerical_feature_value_to_numerical_name(
                "requestArrivalRate", arrival_rate
            )
        )
        servers_feature = self.feature_model.numerical_feature_value_to_numerical_name(
            "servers", servers
        )
        dimmer_feature = self.feature_model.numerical_feature_value_to_numerical_name(
            "dimmer", dimmer
        )

        configuration = pandas.Series(
            pandas.Series(
                0,
                index=self.feature_model.valid_configurations_numerical.drop(
                    columns=["R", "N"]
                ).columns,
            )
        )
        for feature in ["root", "system", "context", "servers", "dimmer"]:
            configuration[feature] = 1
        configuration["requestArrivalRate"] = 1
        configuration[arrival_rate_feature] = 1
        configuration[servers_feature] = 1
        configuration[dimmer_feature] = 1

        # Utility
        maximum_response_time = 0.75  # T
        average_response_time = self.swim_client.get_average_response_time()
        tau = 10
        r_m = 1
        r_o = 1.5
        kappa = 67.4
        if average_response_time <= maximum_response_time:
            reward = tau * arrival_rate * (dimmer * r_o + (1 - dimmer) * r_m)
        else:
            reward = tau * min(0, arrival_rate - kappa) * r_o

        return configuration, reward

    def effector_interface(self, configuration: pandas.Series) -> None:
        print("effector")
        for index, value in configuration.items():
            numerical_sub_features = [
                sub_feature.name
                for _, sub_features in self.feature_model.numerical_sub_features.items()
                for sub_feature in sub_features
            ]
            if value == 1:
                if index in numerical_sub_features:
                    sub_feature = self.feature_model.numerical_feature_name_to_feature(
                        index
                    )

                    if sub_feature.parent.name == "servers":
                        new_servers = sub_feature.get_value()
                    if sub_feature.parent.name == "dimmer":
                        new_dimmer = sub_feature.get_value()

        print(
            f"Servers: {self.servers}, Dimmer: {self.dimmer}, new_servers: {new_servers}, new_dimmer: {new_dimmer}"
        )
        if new_servers < self.servers:
            # remove servers
            for _ in range(self.servers - new_servers):
                self.swim_client.remove_server()
        elif new_servers > self.servers:
            # add servers
            for _ in range(new_servers - self.servers):
                self.swim_client.add_server()
        if new_dimmer != self.dimmer:
            self.swim_client.set_dimmer(new_dimmer)

    def connect_to_simulator(self):
        self.swim_client.connect("localhost", 4242)

    def disconnect_from_simulator(self):
        self.swim_client.disconnect()


class SWIMAdapatationLogic(AdaptationLogic):

    def __init__(
        self,
        simulation_interface: SimulatorInterface,
        cmab: CMAB,
        feature_model: NumericalFM,
    ) -> None:
        super().__init__(simulation_interface, cmab, feature_model)

    def monitor(self) -> tuple[pandas.Series, float]:
        try:
            return self.simulation_interface.sensor_interface()
        except ValueError as err:
            raise

    def delayed_feedback_available(self, adaptation_loop_interval) -> bool:
        time.sleep(adaptation_loop_interval)
        return True

    def analysis_and_plan(self) -> pandas.Series:
        return None

    def execute(self, system_configuration: pandas.Series) -> None:
        self.simulation_interface.effector_interface(
            self.get_only_system(system_configuration)
        )
