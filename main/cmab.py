import numpy as np
import pandas


class CMAB:
    # Contextual Multi Armed Bandit

    def __init__(
        self, valid_configurations: pandas.DataFrame, context_features: list[str]
    ):
        self.valid_configurations = valid_configurations
        self.context_features = context_features

    def select_arm(self, context: pandas.Series):
        pass

    def update_arm(self, configuration: pandas.Series, reward: float):
        pass


class EpsilonGreedy(CMAB):

    def __init__(
        self,
        valid_configurations: pandas.DataFrame,
        context_features: list[str],
        epsilon: float,
    ):

        super().__init__(valid_configurations, context_features)
        self.epsilon = epsilon

        self.valid_configurations["R"] = pandas.Series(
            [0] * valid_configurations.shape[0]
        )
        self.valid_configurations["N"] = pandas.Series(
            [0] * valid_configurations.shape[0]
        )

    def select_arm(self, context):

        columns_to_check = context.index
        mask = (self.valid_configurations[columns_to_check] == context).all(axis=1)
        matching_configs = self.valid_configurations[mask]

        if np.random.rand() < self.epsilon:
            print("--- random")
            return matching_configs.sample().iloc[0]
        else:
            print("--- max")
            return matching_configs.loc(matching_configs["R"].idxmax()).iloc[0]

    def update_arm(self, configuration, reward):

        columns_to_check = configuration.index
        mask = (self.valid_configurations[columns_to_check] == configuration).all(
            axis=1
        )
        matching_config = self.valid_configurations[mask].iloc[0]
        r_old = matching_config
        r_new = 0
        # max_next_reward = 0

        pass


class AdaptiveEpsilonGreedy(EpsilonGreedy):

    def __init__(
        self,
        valid_configurations: pandas.DataFrame,
        context_features: list[str],
        epsilon_start: float,
        epsilon_min: float,
        decay_constant: float,
    ):

        super().__init__(valid_configurations, context_features, epsilon_start)
        self.epsilon_start = epsilon_start
        self.epsilon_min = epsilon_min
        self.decay_constant = decay_constant

    def select_arm(self, context: pandas.Series):
        return super().select_arm(context)

    def update_arm(self, configuration: pandas.Series, reward: float):
        super().update_arm(configuration, reward)
        self.arm_pulls += 1

        # Linear decay
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon_start - self.decay_constant * sum(self.valid_configurations),
        )


class ThompsonSampling(CMAB):

    def __init__(
        self, valid_configurations: pandas.DataFrame, context_features: list[str]
    ):
        super().__init__(valid_configurations, context_features)

    def select_arm(self, context: pandas.Series):
        pass

    def update_arm(self, configuration: pandas.Series, reward: float):
        pass


if __name__ == "__main__":
    from feature_model import FM
    import os

    file_path = os.path.join(os.path.dirname(__file__), "..", "swim", "swim_fm.json")
    feature_model = FM(os.path.abspath(file_path))

    epsilon_greedy = EpsilonGreedy(
        feature_model.valid_valid_configurations_numerical,
        feature_model.context_feature_names,
        0.9,
    )

    test_context = pandas.Series(
        {
            "requestArrivalRate": 1,
            "requestArrivalRate_0": 1,
            "requestArrivalRate_25": 0,
            "requestArrivalRate_50": 0,
            "requestArrivalRate_75": 0,
            "requestArrivalRate_100": 0,
        }
    )

    for _ in range(100):
        selected_config = epsilon_greedy.select_arm(test_context)
        print(selected_config)
        epsilon_greedy.update_arm(selected_config, 5)
        break
