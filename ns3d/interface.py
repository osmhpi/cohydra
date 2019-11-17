import logging
from ns import core, csma, internet, network as ns_net

logger = logging.getLogger(__name__)

class Interface:

    def __init__(self, network, nodes, delay="100Mbps", speed="0ms"):
        self.network = network
        self.nodes = nodes
        self.delay = delay
        self.speed = speed

        self.ns3_nodes_container = None
        self.devices_container = None
        self.csma = csma.CsmaHelper()

    def prepare(self, simulation):
        logging.info('Creating container with %d nodes', len(self.nodes))
        self.ns3_nodes_container = ns_net.NodeContainer()
        for node in self.nodes:
            self.ns3_nodes_container.Add(node.ns3_node())

        logging.info('Install connection between nodes')
        self.csma.SetChannelAttribute("DataRate", core.StringValue(self.speed))
        self.csma.SetChannelAttribute("Delay", core.StringValue(self.delay))
        self.devices_container = self.csma.Install(self.ns3_nodes_container)

        logger.info('Set IP addresses on nodes')

        stack_helper = internet.InternetStackHelper()
        for node_index in range(0, len(self.nodes)):
            node = self.nodes[node_index]
            ns3_node = node.ns3_node()
            device = self.devices_container.Get(node_index)
            if ns3_node.GetObject(internet.Ipv4.GetTypeId()) is None:
                stack_helper.Install(ns3_node)
            device_container = ns_net.NetDeviceContainer(device)
            ip_address = self.network.address_helper.Assign(device_container).GetAddress(0)
            node.prepare(simulation, device, str(ip_address))
        self.csma.EnablePcapAll('./cap', True)
