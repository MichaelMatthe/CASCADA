from models.feature_model import NumericalFM
from models.cmab import EpsilonGreedy
from use_cases.swim.swim_adaptation_logic import (
    SWIMAdapatationLogic,
    SWIMSimulatorInterface,
)


feature_model = NumericalFM("use_cases/swim/swim_fm.json")
cmab_epsilon_greedy = EpsilonGreedy(feature_model, epsilon=0.9, learning_rate=0.1)
swim_simulator_interface = SWIMSimulatorInterface(feature_model)

swim_adaptation_logic = SWIMAdapatationLogic(
    swim_simulator_interface, cmab_epsilon_greedy, feature_model
)

swim_adaptation_logic.run(num_runs=100, adaptation_loop_interval=60)
