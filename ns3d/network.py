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
    """
    A network connects many nodes together and assigns IP addresses.
    It can be compared to a subnet or so.
    """

    def __init__(self, network, netmask=None):
        self.channels = list()
        if isinstance(network, str):
            if '/' in network:
                network = ipaddress.ip_network(network)
            else:
                if netmask is None:
                    netmask = DEFAULT_PREFIX[ipaddress.ip_address(network).version]
                network = ipaddress.ip_network(f'{network}/{netmask}')
        self.network = network
        self.address_helper = network_address_helper(network)
        self.color = None

    def connect(self, *nodes, delay='0ms', speed='100Mbps'):
        """Connects to or more nodes on a single conection.
        This is comparable to inserting a cable between them.
        """
        if len(nodes) < 2:
            raise ValueError('Please specify at least two nodes to connect.')
        channel = Channel(self, nodes, delay=delay, speed=speed)
        self.channels.append(channel)

    def prepare(self, simulation, network_index):
        """Prepares the network by building the docker containers.
        """
        logger.info('Preparing network (base IP: %s)', self.network)

        # Color is needed for NetAnim.
        color = network_color_for(network_index, len(simulation.scenario.networks))
        self.color = color

        channel_index = 0
        for channel in self.channels:
            logger.info('Preparing channel #%d of network %s', channel_index, self.network)
            channel.prepare(simulation)
            channel_index += 1
