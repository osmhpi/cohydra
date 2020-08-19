"""Ethernet LAN channel."""

import logging
import ipaddress
import os

from ns import core, csma, internet, network as ns_net

from .channel import Channel
from ..interface import Interface

logger = logging.getLogger(__name__)

class CSMAChannel(Channel):
    """The Channel resembles a physical connection of nodes.

    For CSMA this would be equivalent to one LAN cable.
    All Nodes connected to a channel will be on one collision domain.

    Parameters
    ----------
    delay : str
        A time for delay in the channel.
    speed : str
        The channel's transmission speed.
    """

    def __init__(self, network, nodes, delay="0ms", speed="100Mbps"):
        super().__init__(network, nodes)

        #: The channel's delay.
        self.delay = delay
        #: The channel's speed for transmitting and receiving.
        #:
        #: Valid values e.g. are :code:`'100Mbps'` or :code:`'64kbps'`.
        self.speed = speed

        #: A helper for connecting nodes via CSMA.
        self.csma_helper = csma.CsmaHelper()

        logger.info('Install connection between nodes')
        self.csma_helper.SetChannelAttribute("DataRate", core.StringValue(self.speed))
        self.csma_helper.SetChannelAttribute("Delay", core.StringValue(self.delay))

        #: All ns-3 devices on this channel.
        self.devices_container = self.csma_helper.Install(self.ns3_nodes_container)

        logger.info('Set IP addresses on nodes')
        stack_helper = internet.InternetStackHelper()

        for i, connected_node in enumerate(nodes):
            ns3_device = self.devices_container.Get(i)
            node = connected_node.node

            address = None
            interface = None
            if node.wants_ip_stack():
                if node.ns3_node.GetObject(internet.Ipv4.GetTypeId()) is None:
                    logger.info('Installing IP stack on %s', node.name)
                    stack_helper.Install(node.ns3_node)
                address = connected_node.address
                if address is None:
                    address = self.network.get_free_ip_address()

                network_address = ipaddress.ip_network(f'{str(address)}/{network.netmask}', strict=False)
                ns3_network_address = ns_net.Ipv4Address(network_address.network_address)
                ns3_network_prefix = ns_net.Ipv4Mask(network_address.netmask)
                base = ipaddress.ip_address(int(address)-int(network_address.network_address))
                helper = internet.Ipv4AddressHelper(ns3_network_address, ns3_network_prefix,
                                                    base=ns_net.Ipv4Address(str(base)))
                device_container = ns_net.NetDeviceContainer(ns3_device)
                helper.Assign(device_container)
                interface = Interface(node=node, ns3_device=ns3_device,
                                      address=ipaddress.ip_interface(f'{str(address)}/{network.netmask}'))
            else:
                interface = Interface(node=node, ns3_device=ns3_device, address=connected_node.address)
            ns3_device.SetAddress(ns_net.Mac48Address(interface.mac_address))
            node.add_interface(interface)
            self.interfaces.append(interface)

    def prepare(self, simulation):
        for interface in self.interfaces:
            pcap_log_path = os.path.join(simulation.log_directory, interface.pcap_file_name)
            self.csma_helper.EnablePcap(pcap_log_path, interface.ns3_device, True, True)
