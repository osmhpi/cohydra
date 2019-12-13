import logging
from pyroute2 import IPRoute
from ns import core, tap_bridge
from .context import defer

logger = logging.getLogger(__name__)

class Interface:
    """! The Interface resembles some kind of network card."""
    __counter = 0

    def __init__(self, node, ns3_device, address):
        """! Create a new interface with a unique name.

        *Warning:* The interface is controlled by the a `Channel`. Do not instantiate
        an Interface by yourself.

        @param node The node to connect the interface to.
        @param ns3_device The ns-3 equivalent of the interface.
        @param address An IP address.
        """
        ## A unique number identifying the interface.
        self.number = Interface.__counter
        Interface.__counter += 1

        ## The node to connect the interface to.
        self.node = node
        ## The ns-3 equivalent of the interface.
        self.ns3_device = ns3_device
        ## The interface's IP
        self.address = address
        ## The name of the interface. This will be set by in `Node.add_interface(...)`.
        self.ifname = None

    def __interface_name(self, prefix):
        """! Return the name of the interface."""
        return f'{prefix}-ns3-{self.number}'

    @property
    def bridge_name(self):
        """! Return a unique name for a bridge."""
        return self.__interface_name('br')

    @property
    def tap_name(self):
        """! Return a unqiue name for a tap."""
        return self.__interface_name('tap')

    @property
    def veth_name(self):
        """! Return a unique name for an VETH pair."""
        return self.__interface_name('veth')

    @property
    def pcap_file_name(self):
        """! Return the name for the PCAP log file-"""
        return f'{self.node.name}.{self.ifname}.pcap'

    def setup_bridge(self):
        """! Setup a bridge for adding a tap later on."""
        ipr = IPRoute()

        logger.debug('Create bridge %s', self.bridge_name)
        ipr.link('add', ifname=self.bridge_name, kind='bridge')
        defer(f'remove bridge {self.bridge_name}', self.remove_bridge)

        ipr.link('set', ifname=self.bridge_name, state='up')

    def remove_bridge(self):
        """! Destroy the bridge-"""
        ipr = IPRoute()

        logger.debug('Remove bridge %s', self.bridge_name)
        ipr.link('del', ifname=self.bridge_name)

    def connect_tap_to_bridge(self, bridge_name=None):
        """! Connect a ns-3 tap device to the bridge.

        @param bridge_name The bridge to connect thetap (and ns-3) device to."""
        if bridge_name is None:
            bridge_name = self.bridge_name

        ipr = IPRoute()

        logger.debug('Connect %s to bridge %s via %s', self.node.name, bridge_name, self.tap_name)
        ipr.link('add', ifname=self.tap_name, kind='tuntap', mode='tap')
        defer(f'disconnect ns3 node {self.node.name}', self.disconnect_tap_from_bridge)

        ipr.link('set', ifname=self.tap_name, state='up')
        ipr.link('set', ifname=self.tap_name, master=ipr.link_lookup(ifname=bridge_name)[0])

        tap_helper = tap_bridge.TapBridgeHelper()
        tap_helper.SetAttribute('Mode', core.StringValue('UseBridge'))
        tap_helper.SetAttribute('DeviceName', core.StringValue(self.tap_name))
        tap_helper.Install(self.node.ns3_node, self.ns3_device)

    def disconnect_tap_from_bridge(self):
        """! Disconnect the (tap) interface and delete it."""
        ipr = IPRoute()

        logger.debug('Disconnect %s from bridge via %s', self.node.name, self.tap_name)
        ipr.link('del', ifname=self.tap_name)

    def setup_veth_pair(self, peer):
        """! Setup a VETH pair for containers.

        This function also connects the external site of the pair to the bridge.

        @param peer Options for the internal side of the VETH pair.
            This can e.g. contain the network namespace (see `DockerNode` for example).
        """
        ipr = IPRoute()

        logger.debug('Create veth pair %s on bridge %s', self.veth_name, self.bridge_name)
        ipr.link('add', ifname=self.veth_name, peer=peer, kind='veth')
        ipr.link('set', ifname=self.veth_name, master=ipr.link_lookup(ifname=self.bridge_name)[0])
        ipr.link('set', ifname=self.veth_name, state='up')

    def setup_veth_container_end(self, ifname):
        """! Setup the VETH in a container.

        @param ifname The interface name within the container.
        """
        ipr = IPRoute()

        logger.debug('Bind veth %s to %s at %s', self.veth_name, ifname, self.address)
        index = ipr.link_lookup(ifname=ifname)[0]
        ipr.addr('add', index=index, address=str(self.address.ip), mask=self.address.network.prefixlen)
        ipr.link('set', index=index, state='up')
