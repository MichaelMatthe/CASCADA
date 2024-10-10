from pathlib import Path
import json

from models.feature_model import NumericalFM
from models.cmab import EpsilonGreedy
from use_cases.swim.swim_client import SwimClient
from use_cases.swim.swim_adaptation_logic import SWIMAdapatationLogic

if True:

    feature_model = NumericalFM("use_cases/swim/swim_fm.json")
    valid_configurations = feature_model.generate_numerical_truth_table()
    context_features = feature_model.context_feature_names

    swim_client = SwimClient()
    swim_client.connect("localhost", 4242)

    cmab_epsilon_greedy = EpsilonGreedy(valid_configurations, context_features, 0.9)

    swim_adaptation_logic = SWIMAdapatationLogic(swim_client, cmab_epsilon_greedy)
