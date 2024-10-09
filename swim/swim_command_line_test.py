import time
from swim.swim_client import SwimClient

if __name__ == "__main__":
    swim_client = SwimClient()
    swim_client.connect("localhost", 4242)

    while True:
        print("servers: {}".format(swim_client.get_servers()))
        input_value = input("Command:")
        if input_value == "exit":
            break
        elif input_value == "add":
            swim_client.add_server()
        elif input_value == "remove":
            swim_client.remove_server()
        elif input_value == "dimmer":
            dimmer_value = float(input("Dimmer value:"))
            swim_client.set_dimmer(dimmer_value)
        elif input_value == "max_servers":
            print(swim_client.get_max_servers())
        else:
            print("Invalid Command")
        time.sleep(0.5)

    swim_client.disconnect()
