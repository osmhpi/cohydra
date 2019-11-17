import logging
from ns import internet, network
from .interface import Interface

class Network:
    """
    A network connects many nodes together and assigns IP addresses.
    It can be compared to a subnet or so.
    """

    def __init__(self, base_ip, subnet_mask):
        self.interfaces = list()
        self.base_ip = base_ip
        self.subnet_mask = subnet_mask
        self.address_helper = None

    def connect(self, *nodes, delay='0ms', speed='100Mbps'):
        """Connects to or more nodes on a single conection.
        This is comparable to inserting a cable between them.
        """
        if len(nodes) < 2:
            raise ValueError('Please specify at least two nodes to connect.')
        interface = Interface(self, nodes, delay=delay, speed=speed)
        for node in nodes:
            node.interfaces.append(interface)
        self.interfaces.append(interface)

    def all_nodes(self):
        node_set = set()
        for interface in self.interfaces:
            node_set = node_set.union(set(interface.nodes))
        return node_set

    def prepare(self):
        """Prepares the network by building the docker containers.
        """
        logging.info('Preparing network (base IP: %s)', self.base_ip)

        self.address_helper = internet.Ipv4AddressHelper(network.Ipv4Address(self.base_ip),
                                                         network.Ipv4Mask(self.subnet_mask))
        interface_index = 0
        for interface in self.interfaces:
            logging.info('Preparing bus #%d of network %s', interface_index, self.base_ip)
            interface.prepare()

    def teardown(self):
        for interface in self.interfaces:
            interface.teardown()
