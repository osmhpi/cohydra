#!/usr/bin/env python3

from ns3d import ArgumentParser, Scenario, Network
from ns3d.node import SSHNode

def main():
    scenario = Scenario()

    net = Network('10.200.0.0', '255.255.255.0')

    ping = SSHNode('ping')
    pong = SSHNode('pong')
    net.connect(ping, pong, delay='150ms', speed='100Mbps')

    scenario.add_network(net)

    with scenario as sim:
        sim.simulate()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
