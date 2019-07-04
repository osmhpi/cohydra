from __future__ import print_function

from netsimbridge.CSMANetwork import CSMANetwork
from netsimbridge.WifiNetwork import WifiNetwork
from netsimbridge.PointToPointNetwork import PointToPointNetwork
from lxdcontainer.LXDContainer import LXDContainer
from events.Event import e
from sumo.SumoSimulation import SumoSimulation
import ns.core
import sys
import math

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

# conleft2 = LXDContainer("left2", "ubuntu:16.04")
# conleft2.create()

conleft.start()
# conleft2.start()
conright.start()

# network = CSMANetwork("net1")
# network = PointToPointNetwork("net1")
network = WifiNetwork("net1")
# network.set_delay(50)
network.set_data_rate("54Mbps")
# network.add_node(conleft, "10.1.1.2", "24", connect_on_create=True)
network.add_node(conleft, 0, 0, 0, "10.1.1.2", "24", connect_on_create=True)
# network.add_node(conleft2, "10.199.199.3", "24")
# network.add_node(conright, "10.1.1.4", "24", connect_on_create=True)
network.add_node(conright, 15, 0, 0, "10.1.1.4", "24", connect_on_create=True)

e().after(30).execute(lambda: network.set_position(conright, 1000, 0, 0)).start_on_simulation_start()
e().after(90).execute(lambda: network.set_position(conright, 10, 0, 0)).start_on_simulation_start()

# e().after(10).execute(lambda: print("After 10 seconds"))\
#     .after(15).execute(lambda: print("After 25 seconds")).start_on_simulation_start()


def after_sumo_simulation_step(simulation, traci):
    dist = simulation.get_distance_between_nodes(conleft, conright)
    network.set_delay(int(math.ceil(dist)))


try:
    network.create()
    # network2 = CSMANetwork("net2")
    # network2.set_delay(50)
    # network2.set_data_rate(100)
    # network2.add_node(conleft, "10.199.200.2", "24")
    # network2.add_node(conleft2, "10.199.200.3", "24")
    # network2.create()

    # sim = SumoSimulation("/home/arne/source/sumo/bin/sumo-gui", "/home/arne/Masterarbeit/SUMO/test.sumocfg")
    # sim.add_node_to_mapping(conleft, "vehicle_0")
    # sim.add_node_to_mapping(conright, "vehicle_2")
    # sim.set_delay(2000)
    # e().after(10).execute(lambda: sim.start(after_sumo_simulation_step)).start_on_simulation_start()

    ns.core.Simulator.Stop(ns.core.Seconds(6000))
    print("Start Simulation")
    ns.core.Simulator.Run(signal_check_frequency=-1)
    print("Simulation stopped")
except:
    print("Unexpected error:", sys.exc_info())
    pass

print("Start cleanup")
ns.core.Simulator.Destroy()

conleft.destroy()
conright.destroy()
# conleft2.destroy()
print("Clean Up Completed")