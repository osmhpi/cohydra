#!/usr/bin/env python3

from cohydra import ArgumentParser, Scenario, Network, SwitchNode, DockerNode, SSHNode

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    node1 = DockerNode('pong', docker_build_dir='./docker/pong')
    node2 = SwitchNode('bridge-1')
    node3 = SSHNode('ping', '10.243.42.11')
    net.connect(node1, node2, delay='200ms')
    net.connect(node2, node3, delay='200ms')

    scenario.add_network(net)
    with scenario as sim:
        # To simulate forever, just do not specifiy the simulation_time parameter.
        sim.simulate(simulation_time=60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
