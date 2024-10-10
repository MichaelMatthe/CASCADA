import numpy as np
import random

import time
from swim.swim_client import SwimClient


class Arm:

    def __init__(self, r, n):
        self.r = r
        self.n = n


class EpsilonGreedyNoFM:

    def __init__(self, context_system_dict, epsilon):
        # For each context, a list of all configurations available
        # For each arm a mean reward value R and
        # the number of times an arm has been played N
        # {C1: {S1: {'R': 0, 'N', 0}, S2: {'R': 0, 'N': 0}...}, C2: {...}, ...}
        self.epsilon = epsilon

        self.context_dict = {}
        for context, system in context_system_dict.items():
            system_dict = {}
            for system_config in system:
                system_dict[(system_config["servers"], system_config["dimmer"])] = Arm(
                    0, 0
                )
            self.context_dict[context] = system_dict

    def select_arm(self, context):

        if np.random.rand() < self.epsilon:
            available_system_configs = self.context_dict[context]
            return random.choice(list(available_system_configs.keys()))
        else:
            context_arms = self.context_dict[context]
            best_arm_config = ""
            best_arm_R = -100
            for config, arm in context_arms.items():
                if arm.r > best_arm_R:
                    best_arm_config = config
                    best_arm_R = arm.r
            return best_arm_config

    def update_arm(self, context, configuration, reward):
        alpha = 0.3
        gamma = 0.9

        r = self.context_dict[context][configuration].r
        n = self.context_dict[context][configuration].n
        max_next_reward = 0
        # TODO context here needs to be derived from the extended context (current Context + chosen Configuration)
        for _, arm in self.context_dict[context].items():
            if arm.r > max_next_reward:
                max_next_reward = arm.r
        self.context_dict[context][configuration].r = r + alpha(
            reward + gamma * max_next_reward - r
        )
        self.context_dict[context][configuration].n = n + 1


class AdaptationLogic:

    MAX_SERVERS = 3
    MAX_REQUEST_RATE = 60
    REQUEST_RATE_INTERVAL_SIZE = 5

    SERVER_BOOTUP = 10

    def __init__(self):

        self.context_system_dict = {}
        configs = []
        for servers in range(1, self.MAX_SERVERS):
            for dimmer in [0.1 + 0.2 * i for i in range(5)]:
                configs.append({"servers": servers, "dimmer": dimmer})
        for context in range(
            int(self.MAX_REQUEST_RATE / self.REQUEST_RATE_INTERVAL_SIZE)
        ):
            context_key = int(context * self.REQUEST_RATE_INTERVAL_SIZE)
            self.context_system_dict[context_key] = configs

    def run(self, num_runs=1):
        swim_client = SwimClient()
        swim_client.connect("localhost", 4242)
        simulator_interface = SwimSimulatorInterfaceNoFM(swim_client)
        epsilon_greedy_cmab = EpsilonGreedyNoFM(self.context_system_dict, 0.9)

        for run in range(num_runs):
            # 1. get context
            monitored_values = simulator_interface.monitor_values()
            print(monitored_values)
            servers = monitored_values.servers
            dimmer = monitored_values.dimmer

            # 2. get best next arm and reconfigure
            if True:
                current_request_arrival_rate = monitored_values.request_arrival_rate
                rounded_RAR = self.round_context_from_monitor(
                    current_request_arrival_rate
                )
                selected_arm = epsilon_greedy_cmab.select_arm(rounded_RAR)

                server_dif = selected_arm[0] - servers
                dimmer_dif = selected_arm[1] - dimmer
                print(
                    "2 selected arm: servers: {}, dimmer: {}".format(
                        selected_arm[0], selected_arm[1]
                    )
                )
                simulator_interface.execute(int(server_dif), float(selected_arm[1]))

            # 3. trigger for monitoring (delayed) - sleep until adapted
            if True:
                print("3 Reconfiguration:")
                # if dimmer changed -> sleep x secs
                if dimmer_dif != 0:
                    print("dimmer reconfig to: {}".format(float(selected_arm[1])))
                # if number of servers changed -> sleep 60 + x secs
                if server_dif > 0:
                    print(
                        "adding server(s): {}, Bootup = {} secs".format(
                            server_dif, self.SERVER_BOOTUP
                        )
                    )
                    time.sleep(self.SERVER_BOOTUP)
                elif server_dif < 0:
                    print("removing server(s): {}, waiting 5 secs".format(server_dif))
                    time.sleep(5)
                print("Monitoring performance")
                time.sleep(1)
                # else sleep Y secs

            # 4. monitor performance
            monitored_values = simulator_interface.monitor_values()
            print("4 Monitored values:", monitored_values)

            # 5. update arms

        swim_client.disconnect()

    def round_context_from_monitor(self, request_rate):
        if request_rate > self.MAX_REQUEST_RATE:
            request_rate = self.MAX_REQUEST_RATE

        rounded_value = (
            request_rate // self.REQUEST_RATE_INTERVAL_SIZE
        ) * self.REQUEST_RATE_INTERVAL_SIZE

        return int(rounded_value)


adaptation_logic = AdaptationLogic()
adaptation_logic.run(20)
