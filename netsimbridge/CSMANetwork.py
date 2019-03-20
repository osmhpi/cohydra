import ns.core
import ns.network
import ns.internet
import ns.mobility
import ns.csma
import ns.applications


class CSMANetwork(object):

    def __init__(self, name):
        self.name = name
        if len(self.name) > 5:
            raise ValueError("Network name can not be longer than 4 characters.")

        self.system_nodes = []
        self.csma_helper = None
        self.devices = None
        self.datarate = 100
        self.delay = 0

    def add_node(self, system_node, ipv4_addr, ipv4_prefix):
        self.system_nodes.append((system_node, ipv4_addr, ipv4_prefix))

    def del_node(self, node):
        pass

    def set_delay(self, delay):
        self.delay = delay

    def set_data_rate(self, data_rate):
        self.datarate = data_rate

    def create(self):
        node_container = ns.network.NodeContainer()
        for i in range(0, len(self.system_nodes)):
            node_container.Add(self.system_nodes[i][0].get_ns3_node())

        self.csma_helper = ns.csma.CsmaHelper()
        self.csma_helper.SetChannelAttribute("DataRate", ns.core.StringValue(str(self.datarate) + "Mbps"))
        self.csma_helper.SetChannelAttribute("Delay", ns.core.StringValue(str(self.delay) + "ms"))
        self.devices = self.csma_helper.Install(node_container)

        for i in range(0, len(self.system_nodes)):
            system_node_tuple = self.system_nodes[i]
            system_node_tuple[0].connect_to_netdevice(self.name, self.devices.Get(i),
                                                      system_node_tuple[1], system_node_tuple[2])

    def destroy(self):
        pass
