#!/usr/bin/env python3

from testbed import ArgumentParser, Network, DockerNode, SwitchNode, Scenario

class Example(object):
    def __init__(self):
        self.some_value = 21

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

    example = Example()

    @scenario.workflow
    def test(workflow):
        workflow.wait_until(lambda: example.some_value, 6, globals(), locals())
        server.go_offline()
        workflow.sleep(10)
        server.go_online()

    @scenario.workflow
    def test2(workflow):
        workflow.sleep(10)
        client1.execute_command('curl server -v')
        example.some_value = 42

    scenario.add_network(net)
    with scenario as sim:
        # To simulate forever, just do not specifiy the time parameter.
        sim.simulate(simluation_time=60)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
