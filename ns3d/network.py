import logging
from ns import core, csma, internet, network
from .interface import Interface

class Network:
    """
    A network connects many nodes together and assigns IP addresses.
    It can be compared to a subnet or so.
    """

    def __init__(self, base_ip, subnet_mask):
        self.nodes = list()
        self.base_ip = base_ip
        self.subnet_mask = subnet_mask
        self.nodes_container = None

        self.csma = csma.CsmaHelper()
        self.csma.SetChannelAttribute("DataRate", core.StringValue("5Mbps"))
        self.csma.SetChannelAttribute("Delay", core.StringValue("200ms"))

        self.devices_container = None
        self.interfaces = None

    def connect(self, *nodes, delay='0ms', speed='100Mbps'):
        """Connects to or more nodes on a single conection.
        This is comparable to inserting a cable between them.
        """
        if len(nodes) < 2:
            raise ValueError('Please specify at least two nodes to connect.')
        interface = Interface(self, nodes, delay, speed)
        for node in nodes:
            if node not in self.nodes:
                self.nodes.append(node)
            node.interfaces.append(interface)

    def prepare(self):
        """Prepares the network by building the docker containers.
        """
        logging.info('Preparing network (base IP: %s)', self.base_ip)
        self.nodes_container = network.NodeContainer()
        self.nodes_container.Create(len(self.nodes))
        self.devices_container = self.csma.Install(self.nodes_container)
        # Install the internet stack on all nodes
        logging.debug('Install internet stack on nodes')
        stack_helper = internet.InternetStackHelper()
        stack_helper.Install(self.nodes_container)
        logging.debug('Set IP addresses on nodes')
        address_helper = internet.Ipv4AddressHelper(network.Ipv4Address(self.base_ip),
                                                    network.Ipv4Mask(self.subnet_mask))
        self.interfaces = address_helper.Assign(self.devices_container)
        for node_index in range(0, len(self.nodes)):
            node = self.nodes[node_index]
            device = self.devices_container.Get(node_index)
            ns3_node = self.nodes_container.Get(node_index)
            node_ip = str(self.interfaces.GetAddress(node_index))
            node.prepare(ns3_node, device, node_ip)

        self.csma.EnablePcapAll('./capture', True)

    def teardown(self):
        for node in self.nodes:
            node.teardown()
