import ns.core
import ns.network
import ns.internet
import ns.mobility
import ns.csma
import ns.applications


class CSMANetwork:

    def __init__(self, size, datarate, delay):
        self.size = size
        self.nodes = ns.network.NodeContainer()
        self.nodes.Create(size)

        self.csmaHelper = ns.csma.CsmaHelper()
        self.csmaHelper.SetChannelAttribute("DataRate", ns.core.StringValue(str(datarate)+"Mbps"))
        self.csmaHelper.SetChannelAttribute("Delay", ns.core.StringValue(str(delay)+"ms"))
        self.devices = self.csmaHelper.Install(self.nodes)
        self.node_counter = 0

    def add_node(self, node, ipv4_addr, ipv4_prefix, broadcast_addr, bridge_addr):
        if self.node_counter >= self.size:
            print("Cannot connect since network is full")
            return
        # netdevice = node.connect_to_netdevice(ipv4_addr, ipv4_prefix, broadcast_addr, bridge_addr)
        print("b1")
        # self.channel.Attach(netdevice)
        print("b2")
        # netdevice.Attach(self.channel)
        print("b3")
        node.connect_to_netdevice(self.nodes.Get(self.node_counter), self.devices.Get(self.node_counter),
                                  ipv4_addr, ipv4_prefix, broadcast_addr, bridge_addr)
        self.node_counter = self.node_counter + 1
        print("b4")

    def del_node(self, node):
        pass

    def set_delay(self, delay):
        self.channel.SetAttribute("Delay", ns.core.StringValue(str(delay)+"ms"))

    def set_data_rate(self, data_rate):
        pass

    def destroy(self):
        pass
