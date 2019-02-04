import random
import pexpect
import subprocess

from ns.network import Node
import ns.tap_bridge

from tuntap.TunTapDevice import TunTapDevice
from bridge.BridgeDevice import BridgeDevice
from libvirtcontainer.LibVirtConnectionManager import LibVirtConnectionManager

class LXCContainer:

    container_definition = '''
        <domain type='lxc'>
          <name>{name}</name>
          <memory unit='KiB'>65536</memory>
          <currentMemory unit='KiB'>65536</currentMemory>
          <vcpu>1</vcpu>
          <os>
            <type>exe</type>
            <init>/sbin/init</init>
          </os>
          <clock offset='utc'/>
          <on_reboot>restart</on_reboot>
          <on_crash>destroy</on_crash>
          <devices>
            <emulator>/usr/lib/libvirt/libvirt_lxc</emulator>
            <filesystem type='mount' accessmode='passthrough'>
              <source dir='/var/lib/lxc/{name}/rootfs'/>
              <target dir='/'/>
            </filesystem>
            <interface type='network'>
              <source network='default'/>
            </interface>
            <console type='pty' />
          </devices>
        </domain>'''

    network_interface_definition = '''
        <interface type='bridge'>
          <mac address='{mac}'/>
          <source bridge='{bridge}'/>
          <ip address='{ip_addr}' family='ipv4' prefix='{ip_prefix}'/>
        </interface>
    '''

    def __init__(self, name):
        self.tun = None
        self.br = None
        self.name = name
        self.node = None
        self.tapbridge = None
        self.domain = None

    def create(self):
        subprocess.call(["lxc-create", "-n", self.name, "-t", "ubuntu", "--", "-r", "bionic", "-a", "amd64"])
        xml = LXCContainer.container_definition.format(name=self.name)
        self.domain = LibVirtConnectionManager.get_connection_to("lxc").defineXML(xml)

    def connect_to_netdevice(self, netdevice, ipv4_addr, ip_prefix):
        # Create Tun-Tap Device and Bridge
        self.tun = TunTapDevice("tun-"+self.name)
        self.tun.create()
        self.tun.up()

        self.br = BridgeDevice("br-"+self.name)
        self.br.create()
        self.br.add_interface(self.tun)
        self.br.up()

        # Create network interface and switch it on
        mac_addr = "52:54:00:%02x:%02x:%02x" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        netxml = LXCContainer.network_interface_definition.format(mac=mac_addr, bridge=self.br.name,
                                                                  ip_addr=ipv4_addr, ip_prefix=ip_prefix)
        self.domain.attachDevice(netxml)
        self.execute_command("ip link set group default up", sudo=True)  # switch all devices on

        print("1")
        # Connect to ns-3
        self.tapbridge = ns.tap_bridge.TapBridgeHelper()
        print("2")
        self.tapbridge.SetAttribute("Mode", ns.core.StringValue("UseLocal"))
        print("3")
        self.tapbridge.SetAttribute("DeviceName", ns.core.StringValue(self.tun.name))
        print("3b")
        self.node = Node()
        print("4")
        self.tapbridge.Install(self.node, netdevice)
        print("5")
        self.node.AddDevice(netdevice)
        print("6")

    def execute_command(self, command, sudo=False):
        child = pexpect.spawn("virsh -c lxc:// console {name}".format(name=self.name))
        #  child.delaybeforesend = None
        try:
            child.expect([".*[Ll]ogin: ", ".*Escape character is \^\]", ".*[Uu]sername: "])
        except:
            pass
        child.sendline("ubuntu")  # username for login

        try:
            child.expect(".*[Pp]assword: ")
        except:
            pass
        child.sendline("ubuntu")  # corresponding password

        try:
            child.expect(".*$: ")
        except:
            pass
        if sudo:
            child.send("sudo ")
        child.sendline(command)

        if sudo:
            child.sendline("ubuntu")  # password to enable sudo rights

        child.sendline("exit")
        try:
            child.expect([".*[Ll]ogin: ", ".*Escape character is \^\]", ".*[Uu]sername: "])
        except:
            pass
        print(child.before)
        print(child.after)
        child.close()

    def start(self):
        self.domain.create()

    def stop(self):
        self.domain.shutdown()

    def destroy(self):
        self.domain.destroy()
        subprocess.call(["lxc-destroy", self.name])
        if self.br:
            self.br.down()
            self.br.destroy()
        if self.tun:
            self.tun.down()
            self.tun.destroy()
