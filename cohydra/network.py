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

def network_address_helper(network, base):
    if network.version == 4:
        if base is None:
            base = "0.0.0.1"
        address = ns_net.Ipv4Address(network.network_address)
        prefix = ns_net.Ipv4Mask(network.netmask)
        return internet.Ipv4AddressHelper(address, prefix, base=ns_net.Ipv4Address(base))
    if network.version == 6:
        if base is None:
            base = "::1"
        address = ns_net.Ipv6Address(network.network_address)
        prefix = ns_net.Ipv6Prefix(network.prefixlen)
        return internet.Ipv6AddressHelper(address, prefix, base=ns_net.Ipv6Address(base))
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
    base : str
        The base / start for the IP-addresses of this network.
        An IPv4 example for this parameter could be :code:`"0.0.0.50"`.
    default_channel_type : class
        The default channel to use.
        This can be one of :class:`.CSMAChannel` or :class:`.WiFiChannel`.
    """

    def __init__(self, network_address, netmask=None, base=None, default_channel_type=CSMAChannel, **kwargs):
        #: All the channels in the network.
        self.channels = list()
        #: The prototypes for the future channels.
        self.channels_prototypes = {"default": (default_channel_type, kwargs)}
        #: The channel type
        self.default_channel_type = default_channel_type
        #: The list of the connected nodes
        self.nodes = {}
        #: The list of already allocated ip addresses
        self.allocated_ip_addresses = list()

        if isinstance(network_address, str):
            if '/' in network_address:
                network_address = ipaddress.ip_network(network_address)
            else:
                if netmask is None:
                    netmask = DEFAULT_PREFIX[ipaddress.ip_address(network_address).version]
                network_address = ipaddress.ip_network(f'{network_address}/{netmask}')
        #: The network's address (containing the subnet mask).
        self.network = network_address
        #: The network's netmask
        self.netmask = netmask
        #: The next potentially free ip address of that network moved by base
        self.next_free_ip = None
        if base is None:
            self.next_free_ip = ipaddress.ip_address(self.network.network_address) + 1
        else:
            self.next_free_ip = ipaddress.ip_address(self.network.network_address) + int(ipaddress.ip_address(base))
        #: The color of the network's nodes in a visualization.
        self.color = None

    def create_channel(self, name, channel_type=None, **channel_kwargs):
        """Adds one named channel prototype to the network.

        Parameters
        ----------
        name : str
            The name of the channel.
        channel_type : str
            The channel type. If set to :code:`None`, the default channel type will be set.
        channel_kwargs : str
            The arguments of the new channel
        """
        if channel_type is None:
            channel_type = self.default_channel_type
        self.channels_prototypes[name] = (channel_type, channel_kwargs)

    def connect(self, node, ip_addr=None, channel_name="default"):
        """Adds one node to the network.

        This is comparable to inserting a cable between them.

        Parameters
        ----------
        node : :class:`.Node`
            The node that should be connected to the network. It must be instance a subclass of :class:`.Node`.
        ip_addr : str
            The IP address of that node. If :code:`None` an random IP from the network will be assigned.
            If not :code:`None` the IP address have to be in the range of the network.
        channel_name : str
            The name of the channel where the node should be connected to. Default is the default channel.
        """
        address = None
        if ip_addr is not None:
            address = ipaddress.ip_address(ip_addr)
            self.allocated_ip_addresses.append(address)
        if channel_name in self.channels_prototypes:
            if channel_name not in self.nodes:
                self.nodes[channel_name] = list()
            self.nodes[channel_name].append(ConnectedNode(node, address))
        else:
            raise ValueError(f"Channel {channel_name} does not exists. You have to create it before.")

    def block_ip_address(self, ip_addr):
        """Blocks an IP address.

        That IP address will not be assigned to any node.

        Parameters
        ----------
        ip_addr : str
            The IP address which will be blocked.
        """
        logger.info('Block the IP address %s in the network %s/%s', ip_addr, self.network, self.netmask)
        address = ipaddress.ip_address(ip_addr)
        if address in self.allocated_ip_addresses:
            raise ValueError(f'IP address {ip_addr} already in use')
        self.allocated_ip_addresses.append(address)

    def get_free_ip_address(self):
        """Get a free ip address.

        This returns an ip address which is not already allocated.
        """
        address = self.next_free_ip
        self.next_free_ip = self.next_free_ip + 1

        while address in self.allocated_ip_addresses:
            address = self.next_free_ip
            self.next_free_ip = self.next_free_ip + 1

        network_of_address = ipaddress.ip_network(f'{address}/{self.netmask}', strict=False)
        if network_of_address.network_address != self.network.network_address:
            raise ValueError("Too many clients in that network")

        self.allocated_ip_addresses.append(address)
        return address

    def prepare(self, simulation, network_index):
        """Prepares the network.

        *Warning:* Don't call this function manually.

        Parameters
        ----------
        simulation : :class:`.Simulation`
            The simulation to prepare the network for.
        network_index : int
            The index of the network (needed for coloring).
        """
        logger.info('Preparing network (base IP: %s)', self.network)

        for channel_index, channel_name in enumerate(self.channels_prototypes):
            if len(self.nodes[channel_name]) < 2:
                raise ValueError(f'Please specify at least two nodes to connect in the channel {channel_name}.')
            channel = self.channels_prototypes[channel_name][0](self, self.nodes[channel_name],
                                                                **self.channels_prototypes[channel_name][1])
            self.channels.append(channel)

            if self.color is None:
                # Color is needed for a visualization.
                color = network_color_for(network_index, len(simulation.scenario.networks))
                self.color = color

            for channel in self.channels:
                logger.info('Preparing channel #%d of network %s', channel_index, self.network)
                channel.prepare(simulation)


class ConnectedNode:
    def __init__(self, node, address):
        self.node = node
        self.address = address
