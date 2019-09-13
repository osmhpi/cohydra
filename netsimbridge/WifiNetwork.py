import ns.core
import ns.network
import ns.internet
import ns.applications
import ns.mobility
import ns.wifi
import ns.wave
import ns.propagation


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
        self.delay = None
        self.data_rate = "OfdmRate6MbpsBW10MHz"
        self.wifi80211pMac = None
        self.wifi80211p = None
        self.propagation_delay_model = None
        self.position_alloc = None

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
        self.position_alloc = ns.mobility.ListPositionAllocator()
        for connected_node in self.system_nodes:
            if connected_node.connect_on_create:
                node_container.Add(connected_node.system_node.get_ns3_node())
                self.position_alloc.Add(connected_node.pos_vector)

        wifi_channel_helper = ns.wifi.YansWifiChannelHelper.Default()
        self.wifi_channel = wifi_channel_helper.Create()

        self.propagation_delay_model = ns.propagation.ConstantSpeedPropagationDelayModel()
        self.wifi_channel.SetAttribute("PropagationDelayModel", ns.core.PointerValue(self.propagation_delay_model))

        self.wave_phy_helper = ns.wifi.YansWifiPhyHelper.Default()
        self.wave_phy_helper.SetChannel(self.wifi_channel)
        self.wave_phy_helper.SetPcapDataLinkType(ns.wifi.WifiPhyHelper.DLT_IEEE802_11)
        self.wifi80211pMac = ns.wave.NqosWaveMacHelper.Default()
        self.wifi80211p = ns.wave.Wifi80211pHelper.Default()

        phy_mode = self.data_rate
        self.wifi80211p.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                                "DataMode", ns.core.StringValue(phy_mode),
                                                "ControlMode", ns.core.StringValue(phy_mode))

        devices = self.wifi80211p.Install(self.wave_phy_helper, self.wifi80211pMac, node_container)
        self.wave_phy_helper.EnablePcap("wave-simple-80211p", devices)

        self.mobility_helper = ns.mobility.MobilityHelper()
        self.mobility_helper.SetMobilityModel("ns3::ConstantPositionMobilityModel")
        self.mobility_helper.SetPositionAllocator(self.position_alloc)
        self.mobility_helper.Install(node_container)

        i = 0
        for k in range(0, len(self.system_nodes)):
            connected_node = self.system_nodes[k]
            if connected_node.connect_on_create:
                connected_node.wifi_netdevice = devices.Get(i)
                connected_node.system_node.connect_to_netdevice(self.name, connected_node.wifi_netdevice,
                                                                connected_node.ipv4_addr,
                                                                connected_node.ipv4_subnetmask,
                                                                connected_node.bridge_connect,
                                                                connected_node.bridge_connect_ip,
                                                                connected_node.bridge_connect_subnetmask)
                i = i + 1
        self.set_delay(self.delay)

    def connect_node(self, node):
        print("Connect node " + node.name + " to network " + self.name)
        connected_node = None
        for k in range(0, len(self.system_nodes)):
            if self.system_nodes[k].system_node.name == node.name:
                connected_node = self.system_nodes[k]
        if connected_node is None:
            print("Node " + node.name + " not found in network " + self.name)
            return
        node_container = ns.network.NodeContainer()
        node_container.Add(connected_node.system_node.get_ns3_node())

        self.position_alloc.Add(connected_node.pos_vector)
        self.mobility_helper.SetPositionAllocator(self.position_alloc)

        devices = self.wifi80211p.Install(self.wave_phy_helper, self.wifi80211pMac, node_container)
        self.wave_phy_helper.EnablePcap("wave-simple-80211p", devices)
        self.mobility_helper.Install(node_container)
        connected_node.wifi_netdevice = devices.Get(0)
        connected_node.system_node.connect_to_netdevice(self.name, connected_node.wifi_netdevice,
                                                        connected_node.ipv4_addr,
                                                        connected_node.ipv4_subnetmask,
                                                        connected_node.bridge_connect,
                                                        connected_node.bridge_connect_ip,
                                                        connected_node.bridge_connect_subnetmask)
        print("8")

    def connect(self):
        print("Connect all unconnected nodes is not supported on wifi-networks so far")

    def disconnect_node(self, node):
        print("Disconnect nodes is not supported on wifi-networks so far")

    def disconnect(self):
        print("Disconnect all nodes is not supported on wifi-networks so far")

    def set_delay(self, delay):
        print("Set delay of network " + self.name + " to " + str(delay))
        self.delay = delay
        if self.propagation_delay_model is not None:
            # Initial setup: 100ms one-way means 1000 m/s speed
            if self.delay == 0:
                self.propagation_delay_model.SetSpeed(299792458)  # Light Speed
            else:
                self.propagation_delay_model.SetSpeed((100.0/delay)*1000.0)

    def set_data_rate(self, data_rate):
        print("Set data rate of network " + self.name + " to " + data_rate)
        self.data_rate = data_rate  # This have no effect after creating the network so far.

    def set_position(self, system_node, pos_x, pos_y, pos_z):
        # print("Set position of " + system_node.name + " to (" + str(pos_x) + ", " + str(pos_y) + ", " + str(pos_z) + ")")
        for conn_node in self.system_nodes:
            if conn_node.system_node.name == system_node.name:
                conn_node.pos_x = pos_x
                conn_node.pos_y = pos_y
                conn_node.pos_z = pos_z
                conn_node.pos_vector = ns.core.Vector(pos_x, pos_y, pos_z)
                mobility = conn_node.system_node.get_ns3_node().GetObject(ns.mobility.MobilityModel.GetTypeId())
                mobility.SetPosition(conn_node.pos_vector)

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