#!/usr/bin/env python3

from cohydra import ArgumentParser, Network, DockerNode, Scenario, WiFiChannel
from cohydra.mobility_input import SUMOMobilityInput

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    switch = DockerNode('switch', docker_build_dir='./docker/sumo', command="java FileServer")
    train = DockerNode('train', docker_build_dir='./docker/sumo', command="java FileClient")
    net.connect(train, switch, channel_type=WiFiChannel, frequency=5860, channel_width=10, tx_power=18.0,
                standard=WiFiChannel.WiFiStandard.WIFI_802_11p, data_rate=WiFiChannel.WiFiDataRate.OFDM_RATE_BW_6Mbps)

    scenario.add_network(net)

    sumo = SUMOMobilityInput(name='Rail-To-X', sumo_cmd="/home/arne/source/sumo/bin/sumo-gui", config_path="/home/arne/Masterarbeit/sumo-scenarios/scenario4/scenario.sumocfg")
    sumo.add_node_to_mapping(switch, 'n0', obj_type='junction')
    sumo.add_node_to_mapping(train, 'train')

    scenario.add_mobility_input(sumo)

    with scenario as sim:
        # To simulate forever, just do not specifiy the simulation_time parameter.
        sim.simulate(simulation_time=30)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
