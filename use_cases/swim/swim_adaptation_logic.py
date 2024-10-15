import pandas

from use_cases.swim.swim_client import SwimClient
from use_cases.adaptation_logic import AdaptationLogic
from models.feature_model import NumericalFM
from models.cmab import CMAB
from use_cases.adaptation_logic import SimulatorInterface


class SWIMSimulatorInterface(SimulatorInterface):

    def __init__(self, feature_model: NumericalFM) -> None:
        super().__init__(feature_model)
        self.swim_client = SwimClient()

    def sensor_interface(self) -> tuple[pandas.Series, float]:

        arrival_rate = self.swim_client.get_arrival_rate()
        if arrival_rate == None:
            raise ValueError("Simulator not connected?")

        servers = self.swim_client.get_servers()
        dimmer = self.swim_client.get_dimmer()

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
        for index, value in configuration.items():
            if value == 1:
                if index in [
                    sub_feature
                    for parent_feature, sub_features in self.feature_model.numerical_sub_features.items()
                    for sub_feature in sub_features
                ]:
                    effector_value = (
                        self.feature_model.numerical_feature_name_to_value_range(index)
                    )
                    print(
                        index,
                        effector_value,
                    )

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

    def delayed_feedback_available(self) -> bool:
        return True

    def analysis_and_plan(self) -> pandas.Series:
        return None

    def execute(self, system_configuration: pandas.Series) -> None:
        self.simulation_interface.effector_interface(
            self.get_only_system(system_configuration)
        )
