#!/usr/bin/env python3

import logging
from ns3d import Network, Node, Scenario

def main():
    logging.basicConfig(level=logging.INFO)
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    node1 = Node('ping', docker_build_dir='./docker/ping')
    node2 = Node('pong', docker_build_dir='./docker/pong')
    net.connect(node1, node2)

    scenario.add_network(net)
    with scenario as sim:
        sim.simulate(60)

if __name__ == "__main__":
    main()
