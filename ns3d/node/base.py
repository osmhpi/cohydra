import logging

import random
from ns import core, csma, network, netanim

logger = logging.getLogger(__name__)

class Node:
    def __init__(self, name):
        for char in name:
            if not (char.isalnum() or char == '-'):
                raise ValueError('Please only supply alphanumeric names and "-"')
        self.channels = list()
        self.name = name

        self.ns3_node = network.Node()
        core.Names.Add(self.name, self.ns3_node)

        self.set_position(random.randint(10, 100), random.randint(10, 100))
        self.color = None

        self.interfaces = dict()
        self.command_executor = None

    def set_position(self, x, y, z=0): # pylint: disable=invalid-name
        netanim.AnimationInterface.SetConstantPosition(self.ns3_node, x, y, z)

    def add_interface(self, interface, name=None, prefix='eth'):
        if name in self.interfaces:
            raise ValueError(f'Interface {name} already added')
        if name is None:
            for i in range(256):
                test = f'ns3-{prefix}{i}'
                if test not in self.interfaces:
                    name = test
                    break
            assert name is not None
        logger.debug('Added interface %s to node %s', name, self.name)
        interface.ifname = name
        self.interfaces[name] = interface

    def prepare(self, simulation):
        raise NotImplementedError

    def wants_ip_stack(self):
        raise NotImplementedError

    def execute_command(self, command, user=None):
        if self.command_executor is None:
            raise NotImplementedError
        self.command_executor.execute(command, user=user)

    def go_offline(self):
        n_devices = self.ns3_node.GetNDevices()
        logger.debug('Go offline: %s (%d devices)', self.name, n_devices)
        for device_index in range(0, n_devices):
            device = self.ns3_node.GetDevice(device_index)
            if isinstance(device, csma.CsmaNetDevice):
                device.SetSendEnable(False)
                device.SetReceiveEnable(False)

    def go_online(self):
        n_devices = self.ns3_node.GetNDevices()
        logger.debug('Go online: %s (%d devices)', self.name, n_devices)
        for device_index in range(0, n_devices):
            device = self.ns3_node.GetDevice(device_index)
            if isinstance(device, csma.CsmaNetDevice):
                device.SetSendEnable(True)
                device.SetReceiveEnable(True)
