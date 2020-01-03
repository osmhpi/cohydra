import logging
import ipaddress
import os

from ns import core, csma, internet, network as ns_net

from .channel import Channel
from ..interface import Interface

logger = logging.getLogger(__name__)

class CSMAChannel(Channel):
    """! The Channel resembles a physical connection of nodes.

    For CSMA this would be equivalent to one LAN cable.
    All Nodes connected to a channel will be on one collision domain.
    """

    def __init__(self, network, nodes, delay="0ms", speed="100Mbps"):
        """! @inheritDocs"""
        super().__init__(network, nodes)

        ## The channel's delay.
        self.delay = delay
        ## The channel's speed for transmitting and receiving.
        #
        # Valid values e.g. are `'100Mbps'` or `'64kbps'`.
        self.speed = speed

        ## A helper for connecting nodes via CSMA.
        self.csma_helper = csma.CsmaHelper()

        logger.info('Install connection between nodes')
        self.csma_helper.SetChannelAttribute("DataRate", core.StringValue(self.speed))
        self.csma_helper.SetChannelAttribute("Delay", core.StringValue(self.delay))

        ## All ns-3 devices on this channel.
        self.devices_container = self.csma_helper.Install(self.ns3_nodes_container)

        logger.info('Set IP addresses on nodes')
        stack_helper = internet.InternetStackHelper()

        for i, node in enumerate(nodes):
            ns3_device = self.devices_container.Get(i)

            address = None
            if node.wants_ip_stack():
                if node.ns3_node.GetObject(internet.Ipv4.GetTypeId()) is None:
                    logger.info('Installing IP stack on %s', node.name)
                    stack_helper.Install(node.ns3_node)
                ip_address = self.network.address_helper.NewAddress()
                netmask = network.network.prefixlen
                address = ipaddress.ip_interface(f'{ip_address}/{netmask}')

            interface = Interface(node=node, ns3_device=ns3_device, address=address)
            node.add_interface(interface)
            self.interfaces.append(interface)

    def prepare(self, simulation):
        """! Prepare the channel enabling logging."""
        for interface in self.interfaces:
            pcap_log_path = os.path.join(simulation.log_directory, interface.pcap_file_name)
            self.csma_helper.EnablePcap(pcap_log_path, interface.ns3_device, True, True)
