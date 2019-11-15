from .interface import Interface
import logging

class Network:
    """
    A network connects many nodes together and assigns IP addresses.
    It can be compared to a subnet or so.
    """

    def __init__(self, base_ip, subnet_mask):
        self.nodes = set()
        self.base_ip = base_ip
        self.subnet_mask = subnet_mask

    def connect(self, *nodes, delay='0ms', speed='100Mbps'):
        """Connects to or more nodes on a single conection.
        This is comparable to inserting a cable between them.
        """
        if len(nodes) < 2:
            raise ValueError('Please specify at least two nodes to connect.')
        interface = Interface(self, nodes, delay, speed)
        for node in nodes:
            self.nodes.add(node)
            node.interfaces.append(interface)

    def prepare(self):
        """Prepares the network by building the docker containers.
        """
        logging.info('Preparing network (base ip: %s)', self.base_ip)
        for node in self.nodes:
            node.prepare()

    def teardown(self):
        for node in self.nodes:
            node.teardown()
