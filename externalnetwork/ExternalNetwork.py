import random
import string
import subprocess

import ns.tap_bridge
import ns.network

from tuntap.TunTapDevice import TunTapDevice
from bridge.BridgeDevice import BridgeDevice


class ExternalNetwork(object):

    def __init__(self, name, interface):
        self.name = name
        if len(self.name) > 5:
            raise ValueError("Network name can not be longer than 5 characters.")

        self.interface = NetworkInterface(interface)
        self.running = True
        self.ns3node = None
        self.tun = None
        self.br = None
        self.tapbridge = None
        self.connected = False

    def get_ns3_node(self):
        if self.ns3node is None:
            self.ns3node = ns.network.Node()
        return self.ns3node

    def create(self):
        print("Create has no effect for external networks")

    def connect_to_netdevice(self, network_name, netdevice, ipv4_addr, ip_prefix):
        if self.connected:
            print("External networks can be connected only once. Abort")
            return
        self.connected = True
        # Create Tun-Tap Device and Bridge
        self.tun = TunTapDevice("tun-"+network_name+"-"+self.name)
        self.tun.create()
        self.tun.up()

        self.br = BridgeDevice("br-"+network_name+"-"+self.name)
        self.br.create()
        self.br.add_interface(self.tun)
        self.br.add_interface(self.interface)
        self.br.up()

        # Connect to ns-3
        self.tapbridge = ns.tap_bridge.TapBridgeHelper()
        self.tapbridge.SetAttribute("Mode", ns.core.StringValue("UseBridge"))
        self.tapbridge.SetAttribute("DeviceName", ns.core.StringValue(self.tun.name))
        self.tapbridge.Install(self.get_ns3_node(), netdevice)

    def execute_command(self, command, sudo=False):
        print("Execute Command has no effect for external networks.")

    def start(self):
        print("Start has no effect for external networks.")

    def stop(self):
        print("Stop has no effect for external networks.")

    def destroy(self):
        print("Destroy external network connection " + self.name)
        if self.br:
            self.br.down()
            self.br.destroy()
        if self.tun:
            self.tun.down()
            self.tun.destroy()


class NetworkInterface(object):

    def __init__(self, interface_name):
        self.name = interface_name
