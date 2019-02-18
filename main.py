from __future__ import print_function

from netsimbridge.CSMANetwork import CSMANetwork
from lxdcontainer.LXDContainer import LXDContainer
from events.After import after
from events.When import when
from events.CheckIf import check_if, every
import ns.core
import sys

# import ns.fd_net_device

# emuHelper = ns.fd_net_device.EmuFdNetDeviceHelper()
# print(type(emuHelper).__dict__)
# print("Import successful")
# exit(0)


def overwrite_content_in_file(path, content):
    f = open(path, "w")
    f.write(content)


def prepare_scenario():
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-call-arptables", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-call-iptables", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-filter-vlan-tagged", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-call-ip6tables", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-filter-pppoe-tagged", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-pass-vlan-input-dev", "0")


prepare_scenario()

ns.core.GlobalValue.Bind("SimulatorImplementationType", ns.core.StringValue("ns3::RealtimeSimulatorImpl"))
ns.core.GlobalValue.Bind("ChecksumEnabled", ns.core.BooleanValue("true"))

conleft = LXDContainer("left", "ubuntu:16.04")
conleft.create()

conright = LXDContainer("right", "ubuntu:16.04")
conright.create()

conleft2 = LXDContainer("left2", "ubuntu:16.04")
conleft2.create()

conleft.start()
conleft2.start()
conright.start()

# after(30).execute(lambda: conleft2.stop())
# after(60).execute(lambda: conleft2.start())
# when(lambda: conleft2.running is False, globals(), locals()).execute(lambda obs, old, new: conleft2.start())
every(2).check_if("ls -la").returns(0).then_execute(lambda: print("ls -la returned 0"))
check_if("pwd").returns(0).then_execute(lambda: print("pwd returned 0"))

try:
    network = CSMANetwork("net1", 3, 100, 300)
    network.add_node(conleft, "10.199.199.2", "24")
    network.add_node(conleft2, "10.199.199.3", "24")
    network.add_node(conright, "10.199.199.4", "24")

    network = CSMANetwork("net2", 2, 100, 50)
    network.add_node(conleft, "10.199.200.2", "24")
    network.add_node(conleft2, "10.199.200.3", "24")

    ns.core.Simulator.Stop(ns.core.Seconds(6000))
    print("Start Simulation")
    ns.core.Simulator.Run(signal_check_frequency=-1)
    print("Simulation stopped")
except:
    print("Unexpected error:", sys.exc_info()[0])
    pass

print("Start cleanup")
ns.core.Simulator.Destroy()

conleft.destroy()
conright.destroy()
conleft2.destroy()
print("Clean Up Completed")