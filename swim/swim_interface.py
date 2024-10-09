from swim.swim_client import SwimClient


class MonitoredValues:

    def __init__(
        self, servers, dimmer, request_arrival_rate, opt_content, response_time
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


class SwimSimulatorInterface:

    def __init__(self, swim_client, feature_model):
        self.swim_client = swim_client
        self.feature_model = feature_model

    def monitor(self):
        valid_features = [
            "root",
            "system",
            "context",
            "servers",
            "dimmer",
            "requestArrivalRate",
        ]
        # system
        servers = self.swim_client.get_active_servers()
        valid_features.append(
            self.feature_model.numerical_feature_value_to_numerical_name(
                "servers", servers
            )
        )
        dimmer = self.swim_client.get_dimmer()
        valid_features.append(
            self.feature_model.numerical_feature_value_to_numerical_name(
                "dimmer", dimmer
            )
        )

        # context
        request_arrival_rate = self.swim_client.get_arrival_rate()
        valid_features.append(
            self.feature_model.numerical_feature_value_to_numerical_name(
                "requestArrivalRate", request_arrival_rate
            )
        )

        system_config = []
        context = []
        for feature, mask in zip(
            self.feature_model.ordered_names,
            self.feature_model.get_system_mask(self.feature_model.ordered_names),
        ):
            if feature in valid_features and mask:
                system_config.append(1)
            elif mask:
                system_config.append(0)

        for feature, mask in zip(
            self.feature_model.ordered_names,
            self.feature_model.get_context_mask(self.feature_model.ordered_names),
        ):
            if feature in valid_features and mask:
                context.append(1)
            elif mask:
                context.append(0)

        # performance / reward
        opt_content = self.swim_client.get_optional_throughput()
        response_time = self.swim_client.get_average_response_time()
        return (
            system_config,
            context,
            {
                "servers": servers,
                "opt_content": opt_content,
                "response_time": response_time,
            },
        )

    def monitor_values(self):
        servers = self.swim_client.get_active_servers()
        dimmer = self.swim_client.get_dimmer()

        # context
        request_arrival_rate = self.swim_client.get_arrival_rate()

        # performance / reward
        opt_content = self.swim_client.get_optional_throughput()
        response_time = self.swim_client.get_average_response_time()

        return MonitoredValues(
            servers, dimmer, request_arrival_rate, opt_content, response_time
        )

    def execute(self, configuration):
        # TODO interpret config
        for config, feature in zip(
            configuration, self.feature_model.get_feature_names()
        ):
            if config == 1:
                pass

        config_servers = 1
        config_dimmer = 1.0

        new_servers = config_servers - self.swim_client.get_active_servers()
        if new_servers > 0:
            for _ in range(new_servers):
                self.swim_client.add_server()
        elif new_servers < 0:
            for _ in range(abs(new_servers)):
                self.swim_client.remove_server()
        if config_dimmer != self.swim_client.get_dimmer():
            self.swim_client.set_dimmer(config_dimmer)


class SwimSimulatorInterfaceNoFM:

    def __init__(self, swim_client):
        self.swim_client = swim_client

    def monitor_values(self):
        servers = self.swim_client.get_active_servers()
        dimmer = self.swim_client.get_dimmer()

        # context
        request_arrival_rate = self.swim_client.get_arrival_rate()

        # performance / reward
        opt_content = self.swim_client.get_optional_throughput()
        response_time = self.swim_client.get_average_response_time()

        return MonitoredValues(
            servers, dimmer, request_arrival_rate, opt_content, response_time
        )

    def execute(self, servers_dif, dimmer):
        if servers_dif > 0:
            for i in range(servers_dif):
                self.swim_client.add_server()
        if servers_dif < 0:
            for i in range(abs(servers_dif)):
                self.swim_client.remove_server()
        self.swim_client.set_dimmer(dimmer)


if __name__ == "__main__":
    client = SwimClient()
    client.connect("localhost", 4242)

    sim_interface = SwimSimulatorInterface(client, "")
    try:
        # client.add_server()
        sim_interface.monitor()
        client.remove_server()
    except TypeError as err:
        print(err)
    # Integrate time step of how long simulation steps last

    client.disconnect()
