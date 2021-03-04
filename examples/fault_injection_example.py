#!/usr/bin/env python3

from cohydra import ArgumentParser, Network, DockerNode, Scenario

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0", base="0.0.0.2")
    net.block_ip_address("10.0.0.1")

    node1 = DockerNode('ping', docker_build_dir='./docker/ping')
    node2 = DockerNode('pong', docker_build_dir='./docker/pong')
    channel = net.create_channel(delay="10ms")
    channel.connect(node1, "10.0.0.17")
    channel.connect(node2)

    scenario.add_network(net)

    @scenario.workflow
    def increase_delay(workflow):
        workflow.sleep(60)
        net.set_delay("50ms")  # Inject a fault by increasing the delay to 400ms

    with scenario as sim:
        # To simulate forever, just do not specifiy the simulation_time parameter.
        sim.simulate(simulation_time=240)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
