import subprocess
import random
import string

from helper.SubnetMaskHelper import subnetmask_to_cidr


class BridgeDevice(object):

    def __init__(self, name):
        self.name = name
        self.interfaces = set()
        self.veth_interface_names = None
        self.is_up = False

    def create(self):
        subprocess.call(["brctl", "addbr", self.name])

    def add_interface(self, interface):
        self.add_interface_name(interface.name)

    def add_interface_name(self, interface_name):
        if interface_name not in self.interfaces:
            subprocess.call(["brctl", "addif", self.name, interface_name])
            self.interfaces.add(interface_name)

    def del_interface(self, interface):
        subprocess.call(["brctl", "delif", self.name, interface.name])
        self.interfaces.remove(interface)

    def up(self):
        subprocess.call(["ifconfig", self.name, "up"])
        self.is_up = True

    def connect_veth(self, veth_ip, veth_mask):
        suffix_length = 7  # TODO: Make sure, that the names are unique
        interface_name1 = "br-veth-" + \
                          ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(suffix_length))
        interface_name2 = "br-veth-" + \
                          ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(suffix_length))
        subprocess.call("sudo ip link add dev " + interface_name1 + " type veth peer name " + interface_name2,
                        shell=True)
        self.veth_interface_names = (interface_name1, interface_name2)

        # Add interface 1 to bridge
        self.add_interface_name(interface_name1)
        # Configure interface 2
        subprocess.call("sudo ip addr add " + veth_ip + "/" + str(subnetmask_to_cidr(veth_mask)) + " dev " +
                        interface_name2, shell=True)

        subprocess.call("sudo ip link set " + self.veth_interface_names[0] + " up", shell=True)
        subprocess.call("sudo ip link set " + self.veth_interface_names[1] + " up", shell=True)

    def down(self):
        subprocess.call(["ifconfig", self.name, "down"])
        self.is_up = False

    def destroy(self):
        if self.is_up:
            self.down()
        subprocess.call(["brctl", "delbr", self.name])

        if self.veth_interface_names is not None:
            # Delete interface 1, the other one will be deleted as well since they are paired.
            subprocess.call("sudo ip link set " + self.veth_interface_names[0] + " down", shell=True)
            subprocess.call("sudo ip link set " + self.veth_interface_names[1] + " down", shell=True)
            subprocess.call("sudo ip link del dev " + self.veth_interface_names[0], shell=True)
