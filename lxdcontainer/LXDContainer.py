import random
import string
import subprocess

import ns.tap_bridge
import ns.network

from tuntap.TunTapDevice import TunTapDevice
from bridge.BridgeDevice import BridgeDevice


class LXDContainer(object):

    def __init__(self, name, image, additional_configs=None):
        self.name = name
        if len(self.name) > 5:
            raise ValueError("Container name can not be longer than 5 characters.")

        self.additional_configs = additional_configs if additional_configs else []
        self.image = image
        self.interfaces = {}
        self.running = False
        self.ns3node = None

    def get_ns3_node(self):
        if self.ns3node is None:
            self.ns3node = ns.network.Node()
        return self.ns3node

    def create(self):
        print("Create container " + self.name)
        subprocess.call(["lxc", "init", self.image, self.name])
        for config in self.additional_configs:
            self._configure_container(config)

    def _configure_container(self, config):
        subprocess.call(["lxc", "config", "set", self.name, config['property'], config['value']])

    def start_interfaces(self):
        for interface_name, interface in self.interfaces.items():
            if not interface.up:
                self.execute_command("ifconfig " + interface_name + " up", True)
                self.execute_command("ip addr add " + interface.ip_addr + " dev " + interface_name, True)
                self.interfaces[interface_name].up = True

    def connect_to_netdevice(self, network_name, netdevice, ipv4_addr, ip_prefix, bridge_connect=False,
                             bridge_connect_ip=None, bridge_connect_mask=None):
        # Generate Network Interface Name
        suffix_length = 5
        interface_name = "vnet-" + network_name + "-" + ''.join(
            random.choice(string.ascii_lowercase) for _ in range(suffix_length))
        while interface_name in self.interfaces:
            interface_name = "vnet-" + network_name + "-" + ''.join(
                random.choice(string.ascii_lowercase) for _ in range(suffix_length))

        interface = NetworkInterface(interface_name, network_name)
        interface.ip_addr = ipv4_addr + "/" + ip_prefix

        # Create Tun-Tap Device and Bridge
        interface.tun = TunTapDevice("tun-"+network_name+"-"+self.name)
        interface.tun.create()
        interface.tun.up()

        interface.br = BridgeDevice("br-"+network_name+"-"+self.name)
        interface.br.create()
        interface.br.add_interface(interface.tun)
        interface.br.up()
        if bridge_connect:
            interface.br.connect_veth(bridge_connect_ip, bridge_connect_mask)

        # Add NIC
        print(subprocess.call(["lxc", "config", "device", "add", self.name, interface_name, "nic",
                               "name=" + interface_name, "nictype=bridged", "parent=" + interface.br.name]))

        # Connect to ns-3
        interface.tapbridge = ns.tap_bridge.TapBridgeHelper()
        interface.tapbridge.SetAttribute("Mode", ns.core.StringValue("UseBridge"))
        interface.tapbridge.SetAttribute("DeviceName", ns.core.StringValue(interface.tun.name))
        interface.tapbridge.Install(self.get_ns3_node(), netdevice)

        self.interfaces[interface_name] = interface
        self.start_interfaces()

    def execute_command(self, command, sudo=False):
        # Always executing as sudo but kept the flag for an consistent interface
        if not sudo:
            print("Commands for LXD containers were always executed as sudo.")
        print("exec: "+str(["lxc", "exec", self.name, "--", command]))
        print(subprocess.call("lxc exec " + self.name + " -- " + command, shell=True))

    def start(self):
        print("Start container " + self.name)
        subprocess.call(["lxc", "start", self.name])
        self.start_interfaces()
        self.running = True

    def stop(self):
        print("Stop container " + self.name)
        subprocess.call(["lxc", "stop", self.name])
        for interface_name in self.interfaces:
            self.interfaces[interface_name].up = False
        self.running = False

    def destroy(self):
        print("Destroy container " + self.name)
        self.stop()
        subprocess.call(["lxc", "delete", self.name])
        for interface_name, interface in self.interfaces.items():
            if interface.br:
                interface.br.down()
                interface.br.destroy()
            if interface.tun:
                interface.tun.down()
                interface.tun.destroy()


class NetworkInterface(object):

    def __init__(self, interface_name, network_name):
        self.interface_name = interface_name
        self.network_name = network_name
        self.ip_addr = None
        self.tun = None
        self.br = None
        self.tapbridge = None
        self.up = False
