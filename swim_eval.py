import os
from models.feature_model import NumericalFM
from models.cmab import EpsilonGreedy
from use_cases.swim.swim_client import SwimClient


if __name__ == "__main__":
    swim_adaptation_logic = SWIMAdapatationLogic()
