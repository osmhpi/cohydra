import logging

from ns import bridge, network

from .base import Node

logger = logging.getLogger(__name__)

class SwitchNode(Node):
    """This is representing a switch between other nodes.
    """

    def __init__(self, name):
        super().__init__(name)
        bridge_helper = bridge.BridgeHelper()
        self.bridge_device = bridge_helper.Install(self.name, network.NetDeviceContainer()).Get(0)

    def add_interface(self, interface, *args, **kwargs): # pylint: disable=arguments-differ
        assert interface.address is None, 'Bridges may not have IP addresses.'
        super().add_interface(interface, *args, **kwargs)
        self.bridge_device.AddBridgePort(interface.ns3_device)

    def prepare(self, simulation):
        pass

    def wants_ip_stack(self):
        return False

    def execute_command(self, command, user=None):
        logger.warning('Can not execute command "%s" on bridge node %s', command, self.name)
