import logging
import ipaddress
import os
from ns import core, csma, internet, network as ns_net
from .interface import Interface

logger = logging.getLogger(__name__)

class Channel:
    """! The Channel resembles a physical connection of nodes.

    For CSMA this would be equivalent to one LAN cable.
    All Nodes connected to a channel will be on one collision domain.
    """

    def __init__(self, network, nodes, delay="0ms", speed="100Mbps"):
        """! Create a new Channel.

        *Warning:* Do not instantiate a channel yourself.
            Use the network's capabilities to link nodes.

        @param network The network this channel belongs to.
        @param nodes The nodes to connect on a physical channel.
        @param delay The channel's delay.
        @param speed The channel's speed.
        """
        ## The network the channel belongs to.
        self.network = network
        ## The channel's delay.
        self.delay = delay
        ## The channel's speed for transmitting and receiving.
        #
        # Valid values e.g. are `'100Mbps'` or `'64kbps'`.
        self.speed = speed
        ## All Interfaces (~network cards) on this channel.
        self.interfaces = []

        ## A helper for connecting nodes via CSMA.
        self.csma_helper = csma.CsmaHelper()

        logger.debug('Creating container with %d nodes', len(nodes))

        ## A container with all ns-3 internal nodes.
        self.ns3_nodes_container = ns_net.NodeContainer()
        for node in nodes:
            self.ns3_nodes_container.Add(node.ns3_node)

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
                device_container = ns_net.NetDeviceContainer(ns3_device)
                ip_address = self.network.address_helper.Assign(device_container).GetAddress(0)
                netmask = network.network.prefixlen
                address = ipaddress.ip_interface(f'{ip_address}/{netmask}')

            interface = Interface(node=node, ns3_device=ns3_device, address=address)
            node.add_interface(interface)
            self.interfaces.append(interface)

    @property
    def nodes(self):
        logger.warning('Channel.nodes is deprecated. Use ??? instead.')
        return list(map(lambda interface: interface.node, self.interfaces))

    def prepare(self, simulation):
        """! Prepare the channel enabling logging."""
        for interface in self.interfaces:
            pcap_log_path = os.path.join(simulation.log_directory, interface.pcap_file_name)
            self.csma_helper.EnablePcap(pcap_log_path, interface.ns3_device, True, True)
