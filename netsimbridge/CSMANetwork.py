import ns.core
import ns.network
import ns.internet
import ns.mobility
import ns.csma
import ns.applications


class CSMANetwork(object):

    def __init__(self, name):
        self.name = name
        if len(self.name) > 4:
            raise ValueError("Network name can not be longer than 4 characters.")

        self.system_nodes = []
        self.csma_helper = None
        self.csma_channel = None
        self.datarate = "100Mbps"
        self.delay = 0

    def add_node(self, system_node, ipv4_addr="255.255.255.255", ipv4_subnetmask="255.255.255.255",
                 bridge_connect=False, bridge_connect_ip="255.255.255.255", bridge_connect_mask="255.255.255.255",
                 connect_on_create=False):
        print("Add node " + system_node.name + " to network " + self.name)
        connected_node = ConnectedNode(system_node)
        connected_node.connect_on_create = connect_on_create
        connected_node.ipv4_addr = ipv4_addr
        connected_node.ipv4_subnetmask = ipv4_subnetmask
        connected_node.bridge_connect = bridge_connect
        connected_node.bridge_connect_ip = bridge_connect_ip
        connected_node.bridge_connect_subnetmask = bridge_connect_mask

        self.system_nodes.append(connected_node)

    def create(self):
        print("Create network " + self.name)
        node_container = ns.network.NodeContainer()
        for connected_node in self.system_nodes:
            node_container.Add(connected_node.system_node.get_ns3_node())

        self.csma_helper = ns.csma.CsmaHelper()
        self.csma_channel = ns.csma.CsmaChannel()
        self.set_delay(self.delay)
        self.set_data_rate(self.datarate)
        devices = self.csma_helper.Install(node_container, self.csma_channel)

        for i in range(0, len(self.system_nodes)):
            connected_node = self.system_nodes[i]
            connected_node.csma_netdevice = devices.Get(i)
            connected_node.system_node.connect_to_netdevice(self.name, connected_node.csma_netdevice,
                                                            connected_node.ipv4_addr,
                                                            connected_node.ipv4_subnetmask,
                                                            connected_node.bridge_connect,
                                                            connected_node.bridge_connect_ip,
                                                            connected_node.bridge_connect_subnetmask)
            connected_node.connected = True
            if connected_node.connect_on_create is False:
                self.disconnect_node(connected_node.system_node)
            else:
                print("Node " + connected_node.system_node.name + " connected to network " + self.name)
        print("Network " + self.name + " created")

    def connect_node(self, node):
        print("Connect node " + node.name + " to network " + self.name)
        found = False
        for connected_node in self.system_nodes:
            if connected_node.system_node.name == node.name:
                found = True
                if connected_node.connected is True:
                    print("The node " + connected_node.system_node.name +
                          " is already connected to network " + self.name)
                else:
                    if connected_node.csma_netdevice is None:
                        print("The network " + self.name + " wasn't created. Call create() first.")
                    else:
                        # Reattach since they all were attached on create
                        self.csma_channel.Reattach(connected_node.csma_netdevice)
                        connected_node.connected = True
                        print("Node " + connected_node.system_node.name + " connected to network " + self.name)

        if found is False:
            print("The node " + node.name + " was never connected!")

    def connect(self):
        print("Connect all unconnected nodes to network " + self.name)
        for connected_node in self.system_nodes:
            if connected_node.connected is False:
                self.connect_node(connected_node.system_node)

    def disconnect_node(self, node):
        print("Disconnect node " + node.name + " from network " + self.name)
        found = False
        for connected_node in self.system_nodes:
            if connected_node.system_node.name == node.name:
                found = True
                if connected_node.connected is False:
                    print("The node " + connected_node.system_node.name +
                          " is not connected to the network " + self.name)
                else:
                    if connected_node.csma_netdevice is None:
                        print("The network " + self.name + " wasn't created. Call create() first.")
                    else:
                        self.csma_channel.Detach(connected_node.csma_netdevice)
                        connected_node.connected = False
                        print("Node " + connected_node.system_node.name + " disconnected from network " + self.name)

        if found is False:
            print("The node " + node.name + " was never connected!")

    def disconnect(self):
        print("Disconnect all connected nodes from network " + self.name)
        for connected_node in self.system_nodes:
            if connected_node.connected is True:
                self.disconnect_node(connected_node.system_node)

    def set_delay(self, delay):
        print("Set delay of network " + self.name + " to " + delay)
        self.delay = delay
        if self.csma_channel is not None:
            ns.core.Config.Set("/ChannelList/" + str(self.csma_channel.GetId()) + "/$ns3::CsmaChannel/Delay",
                               ns.core.StringValue(str(self.delay) + "ms"))

    def set_data_rate(self, data_rate):
        print("Set data rate of network " + self.name + " to " + data_rate)
        self.datarate = data_rate
        if self.csma_channel is not None:
            ns.core.Config.Set("/ChannelList/" + str(self.csma_channel.GetId()) + "/$ns3::CsmaChannel/DataRate",
                               ns.core.StringValue(self.datarate))

        # TODO: Has no effect after simulation starts. Override on devices necessary
        #  for connected_node in self.system_nodes:
        #    if connected_node.csma_netdevice is not None:
        #        ns.core.Config.Set("/NodeList/" + str(connected_node.system_node.get_ns3_node().GetId()) +
        #                           "/DeviceList/" + str(connected_node.csma_netdevice.GetIfIndex()) +
        #                           "/$ns3::CsmaNetDevice/DataRate",
        #                           ns.core.StringValue(self.datarate))

    def destroy(self):
        self.disconnect()


class ConnectedNode(object):

    def __init__(self, system_node):
        self.system_node = system_node
        self.connected = False
        self.connect_on_create = False
        self.ipv4_addr = "255.255.255.255"
        self.ipv4_subnetmask = "255.255.255.255"
        self.bridge_connect = False
        self.bridge_connect_ip = "255.255.255.255"
        self.bridge_connect_subnetmask = "255.255.255.255"
        self.csma_netdevice = None