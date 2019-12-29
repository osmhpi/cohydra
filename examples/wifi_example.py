#!/usr/bin/env python3

from ns3d import ArgumentParser, Network, DockerNode, Scenario, WifiChannel

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    node1 = DockerNode('ping', docker_build_dir='./docker/ping')
    node1.set_position(0, 50, 0)
    node2 = DockerNode('pong', docker_build_dir='./docker/pong')
    node2.set_position(10, 50, 0)
    net.connect(node1, node2, channel_type=WifiChannel)

    scenario.add_network(net)

    # @scenario.workflow
    # def move_node(workflow):
    #     x = 10
    #     node2.go_offline()
    #     workflow.sleep(5)
    #     node2.go_online()
    #     while True:
    #         node2.set_position(x, 50, 0)
    #         x += 2
    #         workflow.sleep(2)

    with scenario as sim:
        # To simulate forever, just do not specifiy the simluation_time parameter.
        sim.simulate(simluation_time=600)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
