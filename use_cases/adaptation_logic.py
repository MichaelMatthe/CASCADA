import pandas
from models.cmab import CMAB


class AdaptationLogic:

    def __init__(self, simulation_client, cmab: CMAB):
        self.simulation_client = simulation_client
        self.cmab = cmab

    def run(self, num_runs=1):

        # 1 get context
        current_context = self.monitor_context()

        # 2 select arm based on context from cmab and reconfigure
        selected_configuration = self.cmab.select_arm(current_context)
        self.excute(selected_configuration)

        # 3 monitoring of performance (delayed?)
        reward = self.monitor_performance()

        # 4 update arm
        current_config = self.get_current_system_context_configuration()
        self.cmab.update_arm(current_config, reward)

        pass

    def monitor_context(self) -> pandas.Series:
        pass

    def excute(self, configuration: pandas.Series) -> None:
        pass

    def monitor_performance(self) -> float:
        pass

    def get_current_system_context_configuration(self) -> pandas.Series:
        pass
