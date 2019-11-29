import logging
import os
from ns import core, csma, internet, network as ns_net

logger = logging.getLogger(__name__)

class Channel:

    def __init__(self, network, nodes, delay="100Mbps", speed="0ms"):
        self.network = network
        self.nodes = nodes
        self.delay = delay
        self.speed = speed

        self.csma = csma.CsmaHelper()

        logger.debug('Creating container with %d nodes', len(self.nodes))

        self.ns3_nodes_container = ns_net.NodeContainer()
        for node in self.nodes:
            self.ns3_nodes_container.Add(node.ns3_node())

        logger.info('Install connection between nodes')
        self.csma.SetChannelAttribute("DataRate", core.StringValue(self.speed))
        self.csma.SetChannelAttribute("Delay", core.StringValue(self.delay))
        self.devices_container = self.csma.Install(self.ns3_nodes_container)

        logger.info('Set IP addresses on nodes')
        self.ip_map = dict()
        self.csma_device_map = dict()
        stack_helper = internet.InternetStackHelper()
        for node_index in range(0, len(self.nodes)):
            node = self.nodes[node_index]
            ns3_node = node.ns3_node()

            # Save CSMA device and ip for later
            device = self.devices_container.Get(node_index)
            self.csma_device_map[node] = device

            if node.wants_ip_stack():
                if ns3_node.GetObject(internet.Ipv4.GetTypeId()) is None:
                    logger.info('Installing IP stack on %s', node.name)
                    stack_helper.Install(ns3_node)
                device_container = ns_net.NetDeviceContainer(device)
                ip_address = self.network.address_helper.Assign(device_container).GetAddress(0)
                self.ip_map[node] = str(ip_address)

    def prepare(self, simulation):
        red = self.network.color[0]
        green = self.network.color[1]
        blue = self.network.color[2]
        node_size = simulation.scenario.netanim_node_size

        for node in self.nodes:
            device = self.csma_device_map[node]
            ip_address = self.ip_map.get(node)

            pcap_file_name = node.pcap_file_name()
            if pcap_file_name is not None:
                pcap_log_path = os.path.join(simulation.log_directory, pcap_file_name)
                self.csma.EnablePcap(pcap_log_path, device, True, True)

            node.prepare(simulation, device, ip_address)
            # Set the color according to the network.
            simulation.animation_interface.UpdateNodeColor(node.ns3_node(), red, green, blue)
            simulation.animation_interface.UpdateNodeSize(node.ns3_node().GetId(), node_size, node_size)
