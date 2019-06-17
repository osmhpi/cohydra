import random
import string
import subprocess

import ns.tap_bridge
import ns.fd_net_device
import ns.internet
import ns.network


class ExternalNode(object):

    def __init__(self, name, interface_name, mac_addr, local_ip, local_mask, remote_ip, gateway):
        self.name = name
        self.interface_name = interface_name
        self.mac_addr = mac_addr
        self.local_ip = local_ip
        self.local_mask = local_mask
        self.remote_ip = remote_ip
        self.gateway = gateway
        self.interfaces = {}
        self.running = True
        self.ns3node = None
        self.emu_fd_netdev = None
        self.emu_fd_netdev_helper = None
        self.init_fd_netdevice()

    def get_ns3_node(self):
        if self.ns3node is None:
            self.ns3node = ns.network.Node()
        return self.ns3node

    def init_fd_netdevice(self):
        self.emu_fd_netdev_helper = ns.fd_net_device.EmuFdNetDeviceHelper()
        self.emu_fd_netdev_helper.SetDeviceName(self.interface_name)
        self.emu_fd_netdev = self.emu_fd_netdev_helper.Install(self.get_ns3_node()).Get(0)
        self.emu_fd_netdev.SetAttribute("Address", ns.core.StringValue(self.mac_addr))

        internet_stack_helper = ns.internet.InternetStackHelper()
        internet_stack_helper.Install(self.get_ns3_node())

        ipv4_obj = self.get_ns3_node().GetObject(ns.internet.Ipv4.GetTypeId())
        interface_number = ipv4_obj.AddInterface(self.emu_fd_netdev)
        print("Interface Number: " + str(interface_number))
        interface_address = ns.internet.Ipv4InterfaceAddress(ns.network.Ipv4Address(self.local_ip),
                                                             ns.network.Ipv4Mask(self.local_mask))
        ipv4_obj.AddAddress(interface_number, interface_address)
        ipv4_obj.SetMetric(interface_number, 1)
        ipv4_obj.SetUp(interface_number)

        routing_helper = ns.internet.Ipv4StaticRoutingHelper()
        route = routing_helper.GetStaticRouting(ipv4_obj)
        route.SetDefaultRoute(ns.network.Ipv4Address(self.gateway), interface_number)

    def create(self):
        print("Create has no effect for external nodes.")

    def connect_to_netdevice(self, network_name, netdevice, ipv4_addr, ip_mask):
        ipv4_obj = self.get_ns3_node().GetObject(ns.internet.Ipv4.GetTypeId())
        interface_number = ipv4_obj.AddInterface(netdevice)
        print("Interface Number 2: " + str(interface_number))
        interface_address = ns.internet.Ipv4InterfaceAddress(ns.network.Ipv4Address(ipv4_addr),
                                                             ns.network.Ipv4Mask(ip_mask))
        ipv4_obj.AddAddress(interface_number, interface_address)
        ipv4_obj.SetMetric(interface_number, 1)
        ipv4_obj.SetUp(interface_number)

    def execute_command(self, command, sudo=False):
        print("Execute command not yet implemented for external nodes")

    def start(self):
        print("Start has no effect for external nodes.")

    def stop(self):
        print("Stop has no effect for external nodes.")

    def destroy(self):
        print("Destroy has no effect for external nodes.")


class NetworkInterface(object):

    def __init__(self, interface_name, network_name):
        self.interface_name = interface_name
        self.network_name = network_name
        self.ip_addr = None
        self.tun = None
        self.br = None
        self.tapbridge = None
        self.up = False
