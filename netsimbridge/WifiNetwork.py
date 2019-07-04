import ns.core
import ns.network
import ns.internet
import ns.applications
import ns.mobility
import ns.wifi
import ns.wave


class WifiNetwork(object):

    def __init__(self, name):
        self.name = name
        if len(self.name) > 4:
            raise ValueError("Network name can not be longer than 4 characters.")

        self.system_nodes = []
        self.wifi_helper = None
        self.wifi_mac_helper = None
        self.wifi_channel = None
        self.wave_phy_helper = None
        self.mobility_helper = None
        self.datarate = "54Mbps"

    def add_node(self, system_node, pos_x, pos_y, pos_z, ipv4_addr="255.255.255.255", ipv4_subnetmask="255.255.255.255",
                 bridge_connect=False, bridge_connect_ip="255.255.255.255", bridge_connect_mask="255.255.255.255",
                 connect_on_create=False):
        print("Add node " + system_node.name + " to network " + self.name)
        connected_node = ConnectedNode(system_node, pos_x, pos_y, pos_z)
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
        position_alloc = ns.mobility.ListPositionAllocator()
        for connected_node in self.system_nodes:
            node_container.Add(connected_node.system_node.get_ns3_node())
            position_alloc.Add(connected_node.pos_vector)

        self.wifi_channel = ns.wifi.YansWifiChannelHelper.Default()
        # self.wifi_channel.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel")
        # self.wifi_channel.AddPropagationLoss("ns3::LogDistancePropagationLossModel",
        #                                     "Exponent", ns.core.DoubleValue(3.0),
        #                                     "ReferenceLoss", ns.core.DoubleValue(0.0459))

        self.wave_phy_helper = ns.wifi.YansWifiPhyHelper.Default()
        self.wave_phy_helper.SetChannel(self.wifi_channel.Create())
        self.wave_phy_helper.SetPcapDataLinkType(ns.wifi.WifiPhyHelper.DLT_IEEE802_11)
        wifi80211pMac = ns.wave.NqosWaveMacHelper.Default()
        wifi80211p = ns.wave.Wifi80211pHelper.Default()

        phy_mode = "OfdmRate6MbpsBW10MHz"
        wifi80211p.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                           "DataMode", ns.core.StringValue(phy_mode),
                                           "ControlMode", ns.core.StringValue(phy_mode))

        devices = wifi80211p.Install(self.wave_phy_helper, wifi80211pMac, node_container)
        self.wave_phy_helper.EnablePcap("wave-simple-80211p", devices)

        self.mobility_helper = ns.mobility.MobilityHelper()
        self.mobility_helper.SetMobilityModel("ns3::ConstantPositionMobilityModel")
        self.mobility_helper.SetPositionAllocator(position_alloc)
        self.mobility_helper.Install(node_container)

        for i in range(0, len(self.system_nodes)):
            connected_node = self.system_nodes[i]
            connected_node.wifi_netdevice = devices.Get(i)
            connected_node.system_node.connect_to_netdevice(self.name, connected_node.wifi_netdevice,
                                                            connected_node.ipv4_addr,
                                                            connected_node.ipv4_subnetmask,
                                                            connected_node.bridge_connect,
                                                            connected_node.bridge_connect_ip,
                                                            connected_node.bridge_connect_subnetmask)

    def connect_node(self, node):
        print("Connect node " + node.name + " to network " + self.name)

    def connect(self):
        print("Connect all unconnected nodes to network " + self.name)

    def disconnect_node(self, node):
        print("Disconnect node " + node.name + " from network " + self.name)

    def disconnect(self):
        print("Disconnect all connected nodes from network " + self.name)

    def set_delay(self, delay):
        print("Set delay of network " + self.name + " to " + str(delay))

    def set_data_rate(self, data_rate):
        print("Set data rate of network " + self.name + " to " + data_rate)

    def set_position(self, system_node, pos_x, pos_y, pos_z):
        print("Set position of " + system_node.name + " to (" + str(pos_x) + ", " + str(pos_y) + ", " + str(pos_z) + ")")
        for conn_node in self.system_nodes:
            if conn_node.system_node.name == system_node.name:
                conn_node.pos_x = pos_x
                conn_node.pos_y = pos_y
                conn_node.pos_z = pos_z
                conn_node.pos_vector = ns.core.Vector(pos_x, pos_y, pos_z)

        node_container = ns.network.NodeContainer()
        position_alloc = ns.mobility.ListPositionAllocator()
        for connected_node in self.system_nodes:
            position_alloc.Add(connected_node.pos_vector)
            node_container.Add(connected_node.system_node.get_ns3_node())
        self.mobility_helper.SetPositionAllocator(position_alloc)
        self.mobility_helper.Install(node_container)

    def destroy(self):
        self.disconnect()


class ConnectedNode(object):

    def __init__(self, system_node, pos_x, pos_y, pos_z):
        self.system_node = system_node
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z
        self.pos_vector = ns.core.Vector(pos_x, pos_y, pos_z)
        self.connected = False
        self.connect_on_create = False
        self.ipv4_addr = "255.255.255.255"
        self.ipv4_subnetmask = "255.255.255.255"
        self.bridge_connect = False
        self.bridge_connect_ip = "255.255.255.255"
        self.bridge_connect_subnetmask = "255.255.255.255"
        self.wifi_netdevice = None