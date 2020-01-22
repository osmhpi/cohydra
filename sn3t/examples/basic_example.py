#!/usr/bin/env python3

from sn3t import ArgumentParser, Network, DockerNode, Scenario

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    node1 = DockerNode('ping', docker_build_dir='./docker/ping')
    node2 = DockerNode('pong', docker_build_dir='./docker/pong')
    net.connect(node1, node2, delay='200ms')

    scenario.add_network(net)

    with scenario as sim:
        # To simulate forever, just do not specifiy the simluation_time parameter.
        sim.simulate(simluation_time=60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
