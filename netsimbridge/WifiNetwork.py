import ns.core
import ns.network
import ns.internet
import ns.applications
import ns.mobility
import ns.wifi
import ns.wave
import ns.propagation
from aexpr import aexpr
import random


def get_random_pos():
    return random.randint(-2 ** 100, 2 ** 100)


class WifiNetwork(object):

    def __init__(self, name):
        self.name = name
        if len(self.name) > 4:
            raise ValueError("Network name can not be longer than 4 characters.")

        self.connected_nodes = []
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

        self.connected_nodes.append(connected_node)

    def create(self):
        print("Create network " + self.name)
        node_container = ns.network.NodeContainer()
        self.position_alloc = ns.mobility.ListPositionAllocator()

        for connected_node in self.connected_nodes:
            system_node = connected_node.system_node
            node_container.Add(system_node.get_ns3_node())
            if connected_node.connect_on_create:
                pos_vector = ns.core.Vector(system_node.position[0], system_node.position[1], system_node.position[2])
            else:
                pos_vector = ns.core.Vector(get_random_pos(), get_random_pos(), get_random_pos())
            connected_node.connected = connected_node.connect_on_create
            self.position_alloc.Add(pos_vector)

            def update_position(obs, old_position, new_position):
                if connected_node.connected:
                    self.set_position(connected_node, new_position[0], new_position[1], new_position[2])

            aexpr(lambda: system_node.position, globals(), locals()).on_change(update_position)

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

        for k in range(0, len(self.connected_nodes)):
            connected_node = self.connected_nodes[k]
            connected_node.wifi_netdevice = devices.Get(k)
            connected_node.system_node.connect_to_netdevice(self.name, connected_node.wifi_netdevice,
                                                            connected_node.ipv4_addr,
                                                            connected_node.ipv4_subnetmask,
                                                            connected_node.bridge_connect,
                                                            connected_node.bridge_connect_ip,
                                                            connected_node.bridge_connect_subnetmask)
        self.set_delay(self.delay)

    def get_connected_node_of_system_node(self, system_node):
        for connected_node in self.connected_nodes:
            if connected_node.system_node.name == system_node.name:
                return connected_node
        return None

    def connect_node(self, node):
        print("Connect " + node.name + " to network " + self.name)
        connected_node = self.get_connected_node_of_system_node(node)
        if connected_node is None:
            print("The node " + node.name + " was never added to the network")
        else:
            if connected_node.connected:
                print("The node " + node.name + " is already connected")
            else:
                connected_node.connected = True
                self.set_position(connected_node, node.position[0], node.position[1], node.position[2])
                print("Connected " + node.name + " to network " + self.name)

    def connect(self):
        print("Connect all unconnected nodes to the network " + self.name)
        for connected_node in self.connected_nodes:
            if not connected_node.connected:
                self.connect_node(connected_node.system_node)

    def disconnect_node(self, node):
        print("Disconnect " + node.name + " from network " + self.name)
        connected_node = self.get_connected_node_of_system_node(node)
        if connected_node is None:
            print("The node " + node.name + " was never added to the network")
        else:
            if not connected_node.connected:
                print("The node " + node.name + " is already disconnected")
            else:
                connected_node.connected = False
                self.set_position(connected_node, get_random_pos(), get_random_pos(), get_random_pos())
                print("Disconnected " + node.name + " from network " + self.name)

    def disconnect(self):
        print("Disconnect all connected nodes from the network " + self.name)
        for connected_node in self.connected_nodes:
            if connected_node.connected:
                self.disconnect_node(connected_node.system_node)

    def set_position(self, connected_node, pos_x, pos_y, pos_z):
        pos_vector = ns.core.Vector(pos_x, pos_y, pos_z)
        mobility = connected_node.system_node.get_ns3_node().GetObject(ns.mobility.MobilityModel.GetTypeId())
        mobility.SetPosition(pos_vector)

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
        self.wifi_netdevice = None