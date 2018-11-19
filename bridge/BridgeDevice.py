import subprocess


class BridgeDevice:

    def __init__(self, name):
        self.name = name
        self.interfaces = set()

    def create(self):
        subprocess.call(["brctl", "addbr", self.name])

    def add_interface(self, interface):
        if not interface in self.interfaces:
            subprocess.call(["brctl", "addif", self.name, interface.name])
            self.interfaces.add(interface)

    def del_interface(self, interface):
        subprocess.call(["brctl", "delif", self.name, interface.name])
        self.interfaces.remove(interface)

    def up(self):
        subprocess.call(["ifconfig", self.name, "up"])

    def down(self):
        subprocess.call(["ifconfig", self.name, "down"])

    def destroy(self):
        subprocess.call(["brctl", "delbr", self.name])
