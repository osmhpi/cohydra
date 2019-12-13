import logging
import ipaddress
from ns import internet, network as ns_net

from .channel import Channel
from .util import network_color_for

logger = logging.getLogger(__name__)

DEFAULT_PREFIX = {
    4: 24,
    6: 64,
}

def network_address_helper(network):
    if network.version == 4:
        address = ns_net.Ipv4Address(network.network_address)
        prefix = ns_net.Ipv4Mask(network.netmask)
        return internet.Ipv4AddressHelper(address, prefix)
    if network.version == 6:
        address = ns_net.Ipv6Address(network.network_address)
        prefix = ns_net.Ipv6Prefix(network.prefixlen)
        return internet.Ipv6AddressHelper(address, prefix)
    raise 'Network version is not IPv4 or IPv6'

class Network:
    """! A network connects many nodes together and assigns IP addresses.

    It can be compared to a subnet or so.
    It should also support IPv6 (untested!).
    """

    def __init__(self, network_address, netmask=None):
        """! Create a new network

        @param network_address The network base address (and optional subnet mask).
            An example for this parameter could be `10.42.42.0/24`.
        @param netmask The networks subnet mask. It can be used to provide a mask
            if not already given in the `network_address` parameter.
        """
        ## All the channels in the network.
        self.channels = list()
        if isinstance(network_address, str):
            if '/' in network_address:
                network_address = ipaddress.ip_network(network_address)
            else:
                if netmask is None:
                    netmask = DEFAULT_PREFIX[ipaddress.ip_address(network_address).version]
                network_address = ipaddress.ip_network(f'{network_address}/{netmask}')
        ## The network's address (containing the subnet mask).
        self.network = network_address
        ## A helper used to generate the neccessary IP addresses.
        self.address_helper = network_address_helper(network_address)
        ## The color of the network's nodes in NetAnim.
        self.color = None

    def connect(self, *nodes, delay='0ms', speed='100Mbps'):
        """! Connects to or more nodes on a single conection.

        This is comparable to inserting a cable between them.

        @param nodes The nodes to connect on one physical connection. These must be instances of subclasses of `Node`.
        @param delay The delay on the physical connection.
            Valid values e.g. are `5ms`, `1s`.
        @param speed The connection speed.
            Valid valus e.g. are `64kbps`, `1000Mbps` and so forth.
        """
        if len(nodes) < 2:
            raise ValueError('Please specify at least two nodes to connect.')
        channel = Channel(self, nodes, delay=delay, speed=speed)
        self.channels.append(channel)

    def prepare(self, simulation, network_index):
        """! Prepares the network by building the docker containers.

        *Warning:* Don't call this function manually.

        @param simulation The simulation to prepare the network for.
        @param The index of the network (needed for coloring).
        """
        logger.info('Preparing network (base IP: %s)', self.network)

        if self.color is None:
            # Color is needed for NetAnim.
            color = network_color_for(network_index, len(simulation.scenario.networks))
            self.color = color

        channel_index = 0
        for channel in self.channels:
            logger.info('Preparing channel #%d of network %s', channel_index, self.network)
            channel.prepare(simulation)
            channel_index += 1
