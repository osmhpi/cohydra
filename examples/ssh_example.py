#!/usr/bin/env python3

from cohydra import ArgumentParser, Scenario, Network, SwitchNode, DockerNode, SSHNode

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0", delay="200ms")

    node1 = DockerNode('pong', docker_build_dir='./docker/pong')
    node2 = SwitchNode('bridge-1')
    node3 = SSHNode('ping', '10.243.42.11')
    net.create_channel("channel1")
    net.create_channel("channel2")
    net.connect(node1, channel_name="channel1")
    net.connect(node2, channel_name="channel1")
    net.connect(node2, channel_name="channel2")
    net.connect(node3, channel_name="channel2")

    scenario.add_network(net)
    with scenario as sim:
        # To simulate forever, just do not specifiy the simulation_time parameter.
        sim.simulate(simulation_time=60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
