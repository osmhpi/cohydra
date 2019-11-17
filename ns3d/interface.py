import logging
from ns import core, csma, internet, network as ns_net

class Interface:

    def __init__(self, network, nodes, delay="100Mbps", speed="0ms"):
        self.network = network
        self.nodes = nodes
        self.delay = delay
        self.speed = speed

        self.nodes_container = None
        self.devices_container = None
        self.interfaces = None
        self.csma = csma.CsmaHelper()
        self.ip_map = dict()

    def prepare(self):
        logging.info('Creating container with %d nodes', len(self.nodes))
        self.nodes_container = ns_net.NodeContainer()
        self.nodes_container.Create(len(self.nodes))

        logging.info('Install connection between nodes')
        self.csma.SetChannelAttribute("DataRate", core.StringValue("100Mbps"))
        self.csma.SetChannelAttribute("Delay", core.StringValue("200ms"))
        self.devices_container = self.csma.Install(self.nodes_container)

        logging.info('Install internet stack on nodes')
        stack_helper = internet.InternetStackHelper()
        stack_helper.Install(self.nodes_container)

        logging.info('Set IP addresses on nodes')

        self.interfaces = self.network.address_helper.Assign(self.devices_container)
        for node_index in range(0, len(self.nodes)):
            node = self.nodes[node_index]
            device = self.devices_container.Get(node_index)
            ns3_node = self.nodes_container.Get(node_index)
            node_ip = str(self.interfaces.GetAddress(node_index))
            node.prepare(ns3_node, device, node_ip)
        self.csma.EnablePcapAll('./cap', True)

    def teardown(self):
        for node in self.nodes:
            node.teardown()
