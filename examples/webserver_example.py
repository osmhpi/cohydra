#!/usr/bin/env python3

from sn3t import ArgumentParser, Network, DockerNode, SwitchNode, Scenario

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    bridge = SwitchNode('br-1')

    server = DockerNode('server', docker_image='httpd:2.4')
    net.connect(server, bridge, delay='0', speed='1000Mbps')

    client1 = DockerNode('client-1', docker_build_dir='./docker/curl-webserver', cpus=0.5, memory="128m")
    client2 = DockerNode('client-2', docker_build_dir='./docker/curl-webserver', cpus=0.5, memory="128m")
    net.connect(client1, bridge, delay='50ms', speed='100Mbps')
    net.connect(client2, bridge, delay='20ms', speed='100Mbps')

    scenario.add_network(net)
    with scenario as sim:
        # To simulate forever, just do not specifiy the time parameter.
        sim.simulate(simluation_time=60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
