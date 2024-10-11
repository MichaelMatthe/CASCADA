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
        arrival_rate_feature = (
            self.feature_model.numerical_feature_value_to_numerical_name(
                "requestArrivalRate", arrival_rate
            )
        )

        context = pandas.Series(
            pandas.Series(0, index=self.feature_model.context_feature_names)
        )
        context["requestArrivalRate"] = 1
        context[arrival_rate_feature] = 1

        reward = 10

        return context, reward

    def effector_interface(self, configuration: pandas.Series) -> None:
        return super().effector_interface(configuration)

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
        return self.simulation_interface.sensor_interface()

    def analysis_and_plan(self) -> pandas.Series:
        return None

    def execute(self, system_configuration: pandas.Series) -> None:
        SimulatorInterface.effector_interface(system_configuration)
