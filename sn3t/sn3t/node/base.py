import logging

import random
from ns import core, csma, network, netanim, wifi

logger = logging.getLogger(__name__)

class Node:
    """! A node represents a computer in the simulation.

    It has a unique name.
    """
    def __init__(self, name):
        """! Create a new Node.

        @param name The unique name of the node consisting only of alphanumeric characters.
        """
        for char in name:
            if not (char.isalnum() or char == '-'):
                raise ValueError('Please only supply alphanumeric names and "-"')
        ## The cannels the node is connected to.
        self.channels = list()
        ## The name of the node.
        self.name = name

        ## The ns-3 internal node.
        self.ns3_node = network.Node()
        core.Names.Add(self.name, self.ns3_node)

        self.set_position(random.randint(10, 100), random.randint(10, 100))
        ## The color of the node used in NetAnim.
        self.color = None

        ## The interfaces (~network cards) of this node.
        self.interfaces = dict()
        ## The command executor for running (shell) commands.
        self.command_executor = None

    def set_position(self, x, y, z=0): # pylint: disable=invalid-name
        """! Set the position of the node in NetAnim.

        @param x The x-position.
        @param y The y-position.
        @param z The z-position.
        """
        netanim.AnimationInterface.SetConstantPosition(self.ns3_node, x, y, z)

    def add_interface(self, interface, name=None, prefix='eth'):
        """! Add an interface to the node.

        *Warning:* Do not call this function manually.
            The functionality is handled by the network and channels.

        @param interface The interface to add.
        @param name The name of the interface.
        @param prefix If no name is supplied, the function works out
            a name by appending a number to the prefix.
        """
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
        # Set the name. The name can e.g. be used in a container.
        interface.ifname = name
        self.interfaces[name] = interface

    def prepare(self, simulation):
        """! Do all neccesary steps to prepare a node for the simulation.

        @param simulation The simulation to prepare the node for.
        """
        raise NotImplementedError

    def wants_ip_stack(self):
        """! Indicates whether a IP stack shall be installed onto the node.

        Installing is handled by the Channel.
        """
        raise NotImplementedError

    def execute_command(self, command, user=None):
        """! Execute a command within the node.

        @param command The command to execute.
        @param user If a user (name) is specified, the command is executed
            as this user. *Warning:* Not all nodes support this feature.
        """
        if self.command_executor is None:
            raise NotImplementedError
        self.command_executor.execute(command, user=user)

    def go_offline(self):
        """! Disconnect the node from all channels."""
        n_devices = self.ns3_node.GetNDevices()
        logger.debug('Go offline: %s (%d devices)', self.name, n_devices)
        for device_index in range(0, n_devices):
            device = self.ns3_node.GetDevice(device_index)
            if isinstance(device, csma.CsmaNetDevice):
                device.SetSendEnable(False)
                device.SetReceiveEnable(False)
            elif isinstance(device, wifi.WifiNetDevice):
                phy = device.GetPhy()
                phy.SetRxGain(-10000)
                phy.SetTxGain(-10000)

    def go_online(self):
        """! Connect the node back to all channels."""
        n_devices = self.ns3_node.GetNDevices()
        logger.debug('Go online: %s (%d devices)', self.name, n_devices)
        for device_index in range(0, n_devices):
            device = self.ns3_node.GetDevice(device_index)
            if isinstance(device, csma.CsmaNetDevice):
                device.SetSendEnable(True)
                device.SetReceiveEnable(True)
            elif isinstance(device, wifi.WifiNetDevice):
                phy = device.GetPhy()
                phy.SetRxGain(0)
                phy.SetTxGain(0)
