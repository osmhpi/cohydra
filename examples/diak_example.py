#!/usr/bin/env python3

from cohydra import ArgumentParser, Network, DockerNode, Scenario, WiFiChannel
from cohydra.mobility_input import SUMOMobilityInput


def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0", base="0.0.0.50")

    car = DockerNode('car', docker_build_dir='./docker/diak/car', command="python car.py")
    cross = DockerNode('cross', docker_build_dir='./docker/diak/cross', command="python cross.py")
    train = DockerNode('train', docker_build_dir='./docker/diak/train', command="python train.py")

    net.connect(car, cross, train, channel_type=WiFiChannel, frequency=5860, channel_width=10, tx_power=18.0,
                standard=WiFiChannel.WiFiStandard.WIFI_802_11p, data_rate=WiFiChannel.WiFiDataRate.OFDM_RATE_BW_6Mbps)

    scenario.add_network(net)

    sumo = SUMOMobilityInput(name='DiAK', sumo_port=8081)
    sumo.add_node_to_mapping(car, 'car')
    sumo.add_node_to_mapping(cross, 'cross')
    sumo.add_node_to_mapping(train, 'train')

    scenario.add_mobility_input(sumo)

    with scenario as sim:
        # To simulate forever, just do not specifiy the simulation_time parameter.
        sim.simulate(simulation_time=600)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
