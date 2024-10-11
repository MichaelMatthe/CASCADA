import pandas
from models.cmab import CMAB
from models.feature_model import NumericalFM


class AdaptationLogic:

    def __init__(
        self,
        simulation_interface: "SimulatorInterface",
        cmab: CMAB,
        feature_model: NumericalFM,
    ) -> None:
        self.simulation_interface = simulation_interface
        self.cmab = cmab

        self.feature_model = feature_model
        self.valid_configurations = self.feature_model.generate_numerical_truth_table()
        self.context_features = self.feature_model.context_feature_names
        self.system_features = self.feature_model.system_feature_names

    def run(self, num_runs=1, adaptation_loop_interval=5):

        self.simulation_interface.connect_to_simulator()

        for run in range(num_runs):
            # 1 Monitor
            current_configuration, reward = self.monitor()
            print(f"--- Monitoring: \n{current_configuration}, \nreward: {reward}")

            if self.delayed_feedback_available():
                # Delayed feedback / reward if latency involved
                self.cmab.update_arm(current_configuration, reward)

                # 2 Analysis and Plan
                selected_configuration = self.cmab.select_arm(current_configuration)

                # 3 Execute
                self.execute(selected_configuration)

            # Function for timing the AL to the given interval

        self.simulation_interface.disconnect_from_simulator()

    def monitor(self) -> tuple[pandas.Series, float]:
        pass

    def delayed_feedback_available(self) -> bool:
        pass

    def analysis_and_plan(self) -> pandas.Series:
        pass

    def execute(self, system_configuration: pandas.Series) -> None:
        pass


class SimulatorInterface:

    def __init__(self, feature_model: NumericalFM) -> None:
        self.feature_model = feature_model

    def sensor_interface(self) -> tuple[pandas.Series, float]:
        # Translate simulator values to pandas.Series Feature Model configuration
        pass

    def effector_interface(self, configuration: pandas.Series) -> None:
        # Translate pandas.Series configuration of Feature Model to simulator values
        pass

    def connect_to_simulator(self) -> None:
        pass

    def disconnect_from_simulator(self) -> None:
        pass
