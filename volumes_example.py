#!/usr/bin/env python3

import os
from ns3d import ArgumentParser, Network, DockerNode, BridgeNode, Scenario

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    bridge = BridgeNode('br-1')

    script_directory = os.path.dirname(os.path.realpath(__file__))
    htdocs_directory = os.path.join(script_directory, 'docker/curl-webserver/htdocs')
    # Always specify absolute paths. You can also set 'rw' as mode.
    # If you are lazy, you can also give `{htdocs_directory: '/root/htdocs'}`, which
    # automatically mounts it as read-write.
    server_volumes = {htdocs_directory: {'bind': '/root/htdocs', 'mode':'ro'}}
    server = DockerNode('server', docker_image='httpd:2.4', volumes=server_volumes)
    net.connect(server, bridge, delay='0', speed='1000Mbps')

    client1 = DockerNode('client-1', docker_build_dir='./docker/curl-webserver', cpus=0.5, memory="128m")
    client2 = DockerNode('client-2', docker_build_dir='./docker/curl-webserver', cpus=0.5, memory="128m")
    net.connect(client1, bridge, delay='50ms', speed='100Mbps')
    net.connect(client2, bridge, delay='20ms', speed='100Mbps')

    scenario.add_network(net)
    with scenario as sim:
        # To simulate forever, just do not specifiy the time parameter.
        sim.simulate(time=60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
