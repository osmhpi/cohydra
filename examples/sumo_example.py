#!/usr/bin/env python3

from ns3d import ArgumentParser, Network, DockerNode, Scenario, WifiChannel
from ns3d.mobility_input import SUMOMobilityInput

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    switch = DockerNode('switch', docker_build_dir='./docker/sumo', command="java FileServer")
    train = DockerNode('train', docker_build_dir='./docker/sumo', command="java FileClient")
    net.connect(train, switch, channel_type=WifiChannel, tx_power=30.0)

    scenario.add_network(net)

    sumo = SUMOMobilityInput('sumo-gui', 'docker/sumo/scenarios/scenario4/scenario.sumocfg', name='Rail-To-X')
    sumo.add_node_to_mapping(switch, 'n0', obj_type='junction')
    sumo.add_node_to_mapping(train, 'train')

    scenario.add_mobility_input(sumo)

    with scenario as sim:
        # To simulate forever, just do not specifiy the simluation_time parameter.
        sim.simulate(simluation_time=30)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
