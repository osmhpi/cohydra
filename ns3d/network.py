import logging
from ns import internet, network
from .channel import Channel

logger = logging.getLogger(__name__)

class Network:
    """
    A network connects many nodes together and assigns IP addresses.
    It can be compared to a subnet or so.
    """

    def __init__(self, base_ip, subnet_mask):
        self.channels = list()
        self.base_ip = base_ip
        self.subnet_mask = subnet_mask
        self.address_helper = internet.Ipv4AddressHelper(network.Ipv4Address(self.base_ip),
                                                         network.Ipv4Mask(self.subnet_mask))

    def connect(self, *nodes, delay='0ms', speed='100Mbps'):
        """Connects to or more nodes on a single conection.
        This is comparable to inserting a cable between them.
        """
        if len(nodes) < 2:
            raise ValueError('Please specify at least two nodes to connect.')
        channel = Channel(self, nodes, delay=delay, speed=speed)
        for node in nodes:
            node.channels.append(channel)
        self.channels.append(channel)

    def all_nodes(self):
        node_set = set()
        for channel in self.channels:
            node_set = node_set.union(set(channel.nodes))
        return node_set

    def prepare(self, simulation):
        """Prepares the network by building the docker containers.
        """
        logger.info('Preparing network (base IP: %s)', self.base_ip)

        channel_index = 0
        for channel in self.channels:
            logger.info('Preparing bus #%d of network %s', channel_index, self.base_ip)
            channel.prepare(simulation)
            channel_index += 1
        