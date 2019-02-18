import ns.core
import ns.network
import ns.internet
import ns.mobility
import ns.csma
import ns.applications


class CSMANetwork(object):

    def __init__(self, name, size, datarate, delay):
        self.name = name
        if len(self.name) > 5:
            raise ValueError("Network name can not be longer than 4 characters.")

        self.size = size
        self.nodes = ns.network.NodeContainer()
        self.nodes.Create(size)

        self.csmaHelper = ns.csma.CsmaHelper()
        self.csmaHelper.SetChannelAttribute("DataRate", ns.core.StringValue(str(datarate)+"Mbps"))
        self.csmaHelper.SetChannelAttribute("Delay", ns.core.StringValue(str(delay)+"ms"))
        self.devices = self.csmaHelper.Install(self.nodes)
        self.node_counter = 0

    def add_node(self, node, ipv4_addr, ipv4_prefix):
        if self.node_counter >= self.size:
            print("Cannot connect since network is full")
            return
        node.connect_to_netdevice(self.name, self.nodes.Get(self.node_counter), self.devices.Get(self.node_counter),
                                  ipv4_addr, ipv4_prefix)
        self.node_counter = self.node_counter + 1

    def del_node(self, node):
        pass

    def set_delay(self, delay):
        self.channel.SetAttribute("Delay", ns.core.StringValue(str(delay)+"ms"))

    def set_data_rate(self, data_rate):
        pass

    def destroy(self):
        pass
