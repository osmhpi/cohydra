#!/usr/bin/env python3

from sn3t import ArgumentParser, Network, DockerNode, Scenario, WiFiChannel

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    node1 = DockerNode('ping', docker_build_dir='./docker/ping', command=["tail", "-f", "/dev/null"])
    node1.set_position(0, 50, 0)
    node2 = DockerNode('pong', docker_build_dir='./docker/pong')
    node2.set_position(5, 50, 0)
    # Also have a look at the WiFiChannel initializer. There are some more options you can configure.
    # E.g. the WiFi standard, transmit power and channel number can be set.
    net.connect(node1, node2, channel_type=WiFiChannel)

    scenario.add_network(net)

    @scenario.workflow
    def move_node(workflow):
        x = 10
        node2.go_offline()
        workflow.sleep(5)
        node2.go_online()
        while True:
            node2.set_position(x, 50, 0)
            x += 2
            workflow.sleep(2)

    with scenario as sim:
        # To simulate forever, just do not specifiy the simluation_time parameter.
        sim.simulate(simluation_time=180)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
