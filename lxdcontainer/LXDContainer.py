import random
import string
import subprocess

import ns.tap_bridge

from tuntap.TunTapDevice import TunTapDevice
from bridge.BridgeDevice import BridgeDevice

class LXDContainer:

    def __init__(self, name, image):
        self.name = name
        if len(self.name) > 5:
            raise ValueError("Container name can not be longer than 5 characters.")

        self.tun = None
        self.br = None
        self.image = image
        self.node = None
        self.tapbridge = None
        self.domain = None
        self.interfaces = []

    def create(self):
        subprocess.call(["lxc", "init", self.image, self.name])

    def connect_to_netdevice(self, network_name, ns3node, netdevice, ipv4_addr, ip_prefix):
        # Create Tun-Tap Device and Bridge
        self.tun = TunTapDevice("tun-"+network_name+"-"+self.name)
        self.tun.create()
        self.tun.up()

        self.br = BridgeDevice("br-"+network_name+"-"+self.name)
        self.br.create()
        self.br.add_interface(self.tun)
        self.br.up()

        # Generate Network Interface Name
        suffix_length = 5
        interface_name = "vnet-" + network_name + "-" + ''.join(random.choice(string.ascii_lowercase) for _ in range(suffix_length))
        while interface_name in self.interfaces:
            interface_name = "vnet-" + network_name + "-" + ''.join(random.choice(string.ascii_lowercase) for _ in range(suffix_length))
        self.interfaces.append(interface_name)

        # Add NIC
        print(subprocess.call(["lxc", "config", "device", "add", self.name, interface_name, "nic",
                               "name="+interface_name, "nictype=bridged", "parent="+self.br.name]))
        self.execute_command("ifconfig " + interface_name + " up")
        self.execute_command("ip addr add " + ipv4_addr + "/" + ip_prefix + " dev " + interface_name)
        self.execute_command("ifconfig eth0 down")

        # Connect to ns-3
        self.tapbridge = ns.tap_bridge.TapBridgeHelper()
        self.tapbridge.SetAttribute("Mode", ns.core.StringValue("UseBridge"))
        self.tapbridge.SetAttribute("DeviceName", ns.core.StringValue(self.tun.name))
        self.tapbridge.Install(ns3node, netdevice)

    def execute_command(self, command, sudo=False):
        print("exec: "+str(["lxc", "exec", self.name, "--", command]))
        if sudo:
            print(subprocess.call("lxc exec " + self.name + " -- sudo " + command, shell=True)) # TODO: Verify that sudo works without password
        else:
            print(subprocess.call("lxc exec " + self.name + " -- " + command, shell=True))

    def start(self):
        subprocess.call(["lxc", "start", self.name])

    def stop(self):
        subprocess.call(["lxc", "stop", self.name])

    def destroy(self):
        self.stop()
        subprocess.call(["lxc", "delete", self.name])
        if self.br:
            self.br.down()
            self.br.destroy()
        if self.tun:
            self.tun.down()
            self.tun.destroy()

