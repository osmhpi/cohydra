#!/usr/bin/env python3

import os

from cohydra import ArgumentParser, Network, DockerNode, SwitchNode, Scenario

def volumes_for_validator(validator_num):
    script_directory = os.path.dirname(os.path.realpath(__file__))
    local_key_path = os.path.join(script_directory, f'../docker/sawtooth-pbft/keys/validator{validator_num}/')
    local_pubkey_path = os.path.join(script_directory, '../docker/sawtooth-pbft/keys/validator-pubkeys/')
    validator_volumes = {local_key_path: '/etc/sawtooth/keys/',
                         local_pubkey_path: '/etc/sawtooth/pubkeys/'}
    return validator_volumes


def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    bridge = SwitchNode('br-1')

    validator1 = DockerNode('validator1', docker_build_dir='./docker',
                            dockerfile='sawtooth-pbft/validator/Dockerfile',
                            exposed_ports={8008:8008}, volumes=volumes_for_validator(1),
                            command=['sawtooth-validator', '-v', '-E', 'tcp://validator1:8800'])
    net.connect(validator1, bridge, delay='5ms', speed='100Mbps')

    validator2 = DockerNode('validator2', docker_build_dir='./docker',
                            dockerfile='sawtooth-pbft/validator/Dockerfile',
                            volumes=volumes_for_validator(2),
                            command=['sawtooth-validator', '-v', '-E', 'tcp://validator2:8800'])
    net.connect(validator2, bridge, delay='5ms', speed='100Mbps')

    validator3 = DockerNode('validator3', docker_build_dir='./docker',
                            dockerfile='sawtooth-pbft/validator/Dockerfile',
                            volumes=volumes_for_validator(3),
                            command='sawtooth-validator -v -E tcp://validator3:8800')
    net.connect(validator3, bridge, delay='5ms', speed='100Mbps')

    validator4 = DockerNode('validator4', docker_build_dir='./docker',
                            dockerfile='sawtooth-pbft/validator/Dockerfile',
                            volumes=volumes_for_validator(4),
                            command='sawtooth-validator -v -E tcp://validator4:8800')
    net.connect(validator4, bridge, delay='5ms', speed='100Mbps')

    scenario.add_network(net)
    with scenario as sim:
        # To simulate forever, just do not specifiy the simulation_time parameter.
        sim.simulate(simulation_time=600)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.run(main)
