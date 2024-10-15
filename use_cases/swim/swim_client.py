import socket


class SwimClient:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def disconnect(self):
        self.sock.close()

    def is_connected(self):
        pass

    def send_command(self, command):
        # socket write command
        total_sent = 0
        while total_sent < len(command):
            sent = self.sock.send(command[total_sent:].encode("utf-8"))
            if sent == 0:
                raise RuntimeError("socket connection broken")
            total_sent = total_sent + sent

        # socket read response
        resp = self.sock.recv(2048)
        return resp.decode("utf-8")
        # error checking

    def probe_float(self, command):
        resp = self.send_command(command)
        try:
            return float(resp)
        except ValueError as err:
            print(err, "SWIM Client probe_float")
            return None

    def probe_int(self, command):
        resp = self.send_command(command)
        try:
            return int(resp)
        except ValueError as err:
            print(err, "SWIM Client probe_int")
            return None

    # probes
    def get_dimmer(self):
        return self.probe_float("get_dimmer\n")

    def get_servers(self):
        return self.probe_int("get_servers\n")

    def get_active_servers(self):
        return self.probe_int("get_active_servers\n")

    def get_max_servers(self):
        return self.probe_int("get_max_servers\n")

    def get_utilization(self, server_id):
        return self.probe_float("get_utilization server{}\n".format(server_id))

    def get_basic_response_time(self):
        return self.probe_float("get_basic_rt\n")

    def get_optional_response_time(self):
        return self.probe_float("get_opt_rt\n")

    def get_basic_throughput(self):
        return self.probe_float("get_basic_throughput\n")

    def get_optional_throughput(self):
        return self.probe_float("get_opt_throughput\n")

    def get_arrival_rate(self):
        return self.probe_float("get_arrival_rate\n")

    # effectors
    def add_server(self):
        return self.send_command("add_server\n")

    def remove_server(self):
        return self.send_command("remove_server\n")

    def set_dimmer(self, dimmer):
        return self.send_command("set_dimmer {}\n".format(dimmer))

    # helper methods
    def get_total_utilization(self):
        utilization = 0
        active_servers = self.get_active_servers()
        # server id starts at 1
        for server_id in range(1, active_servers + 1):
            utilization += self.get_utilization(server_id)
        return utilization

    def get_average_response_time(self):
        basic_throughput = self.get_basic_throughput()
        opt_throughput = self.get_optional_throughput()

        avg_response_time = (
            basic_throughput * self.get_basic_response_time()
            + opt_throughput
            * self.get_optional_response_time()
            / (basic_throughput + opt_throughput)
        )
        return avg_response_time
