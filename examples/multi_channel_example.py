#!/usr/bin/env python3

from cohydra import ArgumentParser, Network, DockerNode, Scenario, WiFiChannel

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0", base="0.0.0.2")
    net.block_ip_address("10.0.0.1")

    node1 = DockerNode('ping', docker_build_dir='./docker/ping')
    node2 = DockerNode('pong', docker_build_dir='./docker/pong')
    node3 = DockerNode('ping2', docker_build_dir='./docker/ping')

    net.connect(node1, "10.0.0.11")
    net.connect(node2, "10.0.0.12")

    net.create_channel("wifi")
    net.connect(node2, "10.0.0.22", channel_name="wifi")
    net.connect(node3, "10.0.0.23", channel_name="wifi")

    scenario.add_network(net)

    with scenario as sim:
        # To simulate forever, just do not specifiy the simulation_time parameter.
        sim.simulate(simulation_time=240)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
