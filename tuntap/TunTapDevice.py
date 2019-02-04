import subprocess


class TunTapDevice:

    def __init__(self, name):
        self.name = name

    def create(self):
        subprocess.call(["tunctl", "-t", self.name])
        subprocess.call(["ifconfig", self.name, "hw", "ether", "00:00:00:00:00:01"])


    def up(self):
        subprocess.call(["ifconfig", self.name, "0.0.0.0", "up"])

    def down(self):
        subprocess.call(["ifconfig", self.name, "down"])

    def destroy(self):
        subprocess.call(["tunctl", "-d", self.name])
