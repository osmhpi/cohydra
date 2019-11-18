#!/usr/bin/env python3

import logging
from ns3d import Network, DockerNode, BridgeNode, Scenario

def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('ns3d').setLevel(logging.DEBUG)
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    bridge = BridgeNode('br-1')

    server = DockerNode('server', docker_image='httpd:2.4')
    net.connect(server, bridge, delay='0', speed='1000Mbps')

    client1 = DockerNode('client-1', docker_build_dir='./docker/curl-webserver')
    client2 = DockerNode('client-2', docker_build_dir='./docker/curl-webserver')
    net.connect(client1, bridge, delay='50ms', speed='100Mbps')
    net.connect(client2, bridge, delay='20ms', speed='100Mbps')

    scenario.add_network(net)
    with scenario as sim:
        # To simulate forever, just do not specifiy the time parameter.
        sim.simulate(time=60)

if __name__ == "__main__":
    main()
