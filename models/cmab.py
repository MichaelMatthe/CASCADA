import numpy as np
import pandas

from models.feature_model import NumericalFM

REWARD = "R"
NUMBER_PULLS = "N"


class CMAB:
    # Contextual Multi Armed Bandit

    def __init__(self, feature_model: NumericalFM):
        self.valid_configurations = feature_model.valid_configurations_numerical
        self.context_features = feature_model.context_feature_names

    def select_arm(self, configuration: pandas.Series) -> pandas.Series:
        pass

    def update_arm(self, configuration: pandas.Series, reward: float):
        pass


class EpsilonGreedy(CMAB):

    def __init__(
        self,
        feature_model: NumericalFM,
        epsilon: float,
    ):

        super().__init__(feature_model)
        self.epsilon = epsilon

        self.valid_configurations[REWARD] = pandas.Series(
            [0] * self.valid_configurations.shape[0]
        )
        self.valid_configurations[NUMBER_PULLS] = pandas.Series(
            [0] * self.valid_configurations.shape[0]
        )

    def select_arm(self, configuration):
        # extract context
        context = configuration.loc[self.context_features]

        columns_to_check = context.index
        mask = (self.valid_configurations[columns_to_check] == context).all(axis=1)
        matching_configs = self.valid_configurations[mask]

        if np.random.rand() < self.epsilon:
            print("--- random")
            return matching_configs.sample().iloc[0]
        else:
            print("--- max")
            best_config = matching_configs.loc[matching_configs[REWARD].idxmax()].drop(
                ["R", "N"]
            )
            return best_config

    def update_arm(self, configuration: pandas.Series, reward: float) -> None:

        columns_to_check = configuration.index
        mask = (self.valid_configurations[columns_to_check] == configuration).all(
            axis=1
        )
        matching_config = self.valid_configurations[mask].iloc[0]
        r_old = matching_config
        r_new = 0
        # max_next_reward = 0

        pass


class AdaptiveEpsilonGreedy(CMAB):

    def __init__(
        self,
        feature_model: NumericalFM,
        epsilon_start: float,
        epsilon_min: float,
        decay_constant: float,
    ):

        super().__init__(feature_model)
        self.epsilon_start = epsilon_start
        self.epsilon_min = epsilon_min
        self.decay_constant = decay_constant

    def select_arm(self, configuration: pandas.Series):
        return super().select_arm(configuration)

    def update_arm(self, configuration: pandas.Series, reward: float):
        super().update_arm(configuration, reward)
        self.arm_pulls += 1

        # Linear decay
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon_start - self.decay_constant * sum(self.valid_configurations),
        )


class ThompsonSampling(CMAB):

    def __init__(self, feature_model: NumericalFM):
        super().__init__(feature_model)

    def select_arm(self, context: pandas.Series):
        pass

    def update_arm(self, configuration: pandas.Series, reward: float):
        pass
