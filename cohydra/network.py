"""A subnet."""

import logging
import ipaddress
from ns import internet, network as ns_net

from .channel import CSMAChannel
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
    """A network connects many nodes together and assigns IP addresses.

    It can be compared to a subnet or so.
    It should also support IPv6 (untested!).

    Parameters
    ----------
    network_address : str
        The network base address (and optional subnet mask).
        An example for this parameter could be :code:`"10.42.42.0/24"`.
    netmask : str
        The networks subnet mask. It can be used to provide a mask
        if not already given in the :code:`network_address` parameter.
    """

    def __init__(self, network_address, netmask=None):
        #: All the channels in the network.
        self.channels = list()
        if isinstance(network_address, str):
            if '/' in network_address:
                network_address = ipaddress.ip_network(network_address)
            else:
                if netmask is None:
                    netmask = DEFAULT_PREFIX[ipaddress.ip_address(network_address).version]
                network_address = ipaddress.ip_network(f'{network_address}/{netmask}')
        #: The network's address (containing the subnet mask).
        self.network = network_address
        #: A helper used to generate the neccessary IP addresses.
        self.address_helper = network_address_helper(network_address)
        #: The color of the network's nodes in a visualization.
        self.color = None

    def connect(self, *nodes, channel_type=CSMAChannel, **kwargs):
        """Connects to or more nodes on a single conection.

        This is comparable to inserting a cable between them.
        Necessary configuration can be passed to the channel creation with keyword arguments.

        Parameters
        ----------
        nodes : list of :class:`.Node`
            The nodes to connect on one physical connection. These must be instances of subclasses of :class:`.Node`.
        channel_type : class
            The channel to use.
            This can be one of :class:`.CSMAChannel` or :class:`.WiFiChannel`.
        """
        if len(nodes) < 2:
            raise ValueError('Please specify at least two nodes to connect.')
        channel = channel_type(self, nodes, **kwargs)
        self.channels.append(channel)

    def prepare(self, simulation, network_index):
        """Prepares the network by building the docker containers.

        *Warning:* Don't call this function manually.

        Parameters
        ----------
        simulation : :class:`.Simulation`
            The simulation to prepare the network for.
        network_index : int
            The index of the network (needed for coloring).
        """
        logger.info('Preparing network (base IP: %s)', self.network)

        if self.color is None:
            # Color is needed for a visualization.
            color = network_color_for(network_index, len(simulation.scenario.networks))
            self.color = color

        channel_index = 0
        for channel in self.channels:
            logger.info('Preparing channel #%d of network %s', channel_index, self.network)
            channel.prepare(simulation)
            channel_index += 1
