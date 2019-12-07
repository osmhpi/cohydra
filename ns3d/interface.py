import logging
from pyroute2 import IPRoute
from ns import core, tap_bridge
from .context import defer

logger = logging.getLogger(__name__)

class Interface:
    __counter = 0

    def __init__(self, node, ns3_device, address):
        self.number = Interface.__counter
        Interface.__counter += 1

        self.node = node
        self.ns3_device = ns3_device
        self.address = address
        self.ifname = None

    def interface_name(self, prefix):
        return f'{prefix}-ns3-{self.number}'

    @property
    def bridge_name(self):
        return self.interface_name('br')

    @property
    def tap_name(self):
        return self.interface_name('tap')

    @property
    def veth_name(self):
        return self.interface_name('veth')

    @property
    def pcap_file_name(self):
        return f'{self.node.name}.{self.ifname}.pcap'

    def setup_bridge(self):
        ipr = IPRoute()

        logger.debug('Create bridge %s', self.bridge_name)
        ipr.link('add', ifname=self.bridge_name, kind='bridge')
        defer(f'remove bridge {self.bridge_name}', self.remove_bridge)

        ipr.link('set', ifname=self.bridge_name, state='up')

    def remove_bridge(self):
        ipr = IPRoute()

        logger.debug('Remove bridge %s', self.bridge_name)
        ipr.link('del', ifname=self.bridge_name)

    def connect_ns3_device(self, bridge_name=None):
        if bridge_name is None:
            bridge_name = self.bridge_name

        ipr = IPRoute()

        logger.debug('Connect %s to bridge %s via %s', self.node.name, bridge_name, self.tap_name)
        ipr.link('add', ifname=self.tap_name, kind='tuntap', mode='tap')
        defer(f'disconnect ns3 node {self.node.name}', self.disconnect_ns3_device)

        ipr.link('set', ifname=self.tap_name, state='up')
        ipr.link('set', ifname=self.tap_name, master=ipr.link_lookup(ifname=bridge_name)[0])

        tap_helper = tap_bridge.TapBridgeHelper()
        tap_helper.SetAttribute('Mode', core.StringValue('UseBridge'))
        tap_helper.SetAttribute('DeviceName', core.StringValue(self.tap_name))
        tap_helper.Install(self.node.ns3_node, self.ns3_device)

    def disconnect_ns3_device(self):
        ipr = IPRoute()

        logger.debug('Disconnect %s from bridge via %s', self.node.name, self.tap_name)
        ipr.link('del', ifname=self.tap_name)

    def setup_veth_pair(self, peer):
        ipr = IPRoute()

        logger.debug('Create veth pair %s on bridge %s', self.veth_name, self.bridge_name)
        ipr.link('add', ifname=self.veth_name, peer=peer, kind='veth')
        ipr.link('set', ifname=self.veth_name, master=ipr.link_lookup(ifname=self.bridge_name)[0])
        ipr.link('set', ifname=self.veth_name, state='up')

    def setup_veth_other_end(self, ifname):
        ipr = IPRoute()

        logger.debug('Bind veth %s to %s at %s', self.veth_name, ifname, self.address)
        index = ipr.link_lookup(ifname=ifname)[0]
        ipr.addr('add', index=index, address=str(self.address.ip), mask=self.address.network.prefixlen)
        ipr.link('set', index=index, state='up')
