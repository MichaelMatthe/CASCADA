import os
from main.feature_model import FM


class SWIMAdapatationLogic:

    def __init__(self):
        # feature model
        self.feature_model = FM("swim_fm.json")
        valid_configurations = self.feature_model.generate_numerical_truth_table()


if __name__ == "__main__":
    swim_adaptation_logic = SWIMAdapatationLogic()
