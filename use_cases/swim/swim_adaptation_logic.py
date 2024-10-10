from use_cases.swim.swim_client import SwimClient
from use_cases.adaptation_logic import Adaptation_logic


class MonitoredValues:

    def __init__(
        self,
        servers: int,
        dimmer: float,
        request_arrival_rate: float,
        opt_content: float,
        response_time: float,
    ):
        self.servers = servers
        self.dimmer = dimmer
        self.request_arrival_rate = request_arrival_rate
        self.opt_content = opt_content
        self.response_time = response_time

    def __str__(self):
        return "servers: {}, dimmer: {}, request_arrival_rate: {}, opt_content: {}, response_time: {}".format(
            self.servers,
            self.dimmer,
            self.request_arrival_rate,
            self.opt_content,
            self.response_time,
        )


class SWIMAdapatationLogic(AdaptationLogic):

    def __init__(
        self, configuration_space: pandas.DataFrame, simulation_client, cmab: CMAB
    ):
        # feature model
        self.feature_model = FM("swim_fm.json")
        valid_configurations = self.feature_model.generate_numerical_truth_table()

    def monitor_context(self) -> pandas.Series:
        pass

    def excute(self, configuration: pandas.Series) -> None:
        pass

    def monitor_performance(self) -> float:
        pass

    def get_current_system_context_configuration(self) -> pandas.Series:
        pass
