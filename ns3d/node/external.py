import logging

from ..context import defer
from ..command_executor import ConsoleCommandExecutor
from .base import Node

logger = logging.getLogger(__name__)

class ExternalNode(Node):
    """An external node is representing an external device.
    """

    def __init__(self, name, bridge=None, ifname='eth0'):
        super().__init__(name)

        if bridge is None:
            bridge = f'ns3-{name}'
        self.bridge = bridge
        self.ifname = ifname

        self.command_executor = ConsoleCommandExecutor(self.name)

    def wants_ip_stack(self):
        return True

    def prepare(self, simulation):
        for interface in self.interfaces.values():
            interface.connect_ns3_device(bridge_name=self.bridge)
            self.setup_remote_address(interface.address)

    def setup_remote_address(self, address):
        self.execute_command(['ip', 'addr', 'add', str(address), 'dev', self.ifname], user='root')
        defer(f'remove remote ip {address}', self.remove_remote_address, address)

    def remove_remote_address(self, address):
        self.execute_command(['ip', 'addr', 'del', str(address), 'dev', self.ifname], user='root')
