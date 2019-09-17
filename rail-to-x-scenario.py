from __future__ import print_function

from netsimbridge.WifiNetwork import WifiNetwork
from lxdcontainer.LXDContainer import LXDContainer
from events.Event import e
from sumo.SumoSimulation import SumoSimulation
import ns.core
import sys


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

swtch = LXDContainer("swtch", "java")
swtch.create()

train = LXDContainer("train", "java")
train.create()

swtch.start()
train.start()

network = WifiNetwork("net1")
network.set_delay(0)
network.add_node(swtch, 0, 0, 0, "10.1.1.2", "24", connect_on_create=True)
network.add_node(train, 1000, 0, 0, "10.1.1.4", "24", connect_on_create=True)
network.create()

sim = SumoSimulation("/home/arne/source/sumo/bin/sumo-gui", "/home/arne/Masterarbeit/SUMO/scenario3/test.sumocfg")
sim.add_node_to_mapping(swtch, "n0", "junction")
sim.add_node_to_mapping(train, "vehicle_2")


def after_sumo_simulation_step(simulation, traci):
    l_x, l_y = simulation.get_position_of_node(swtch)
    network.set_position(swtch, int(l_x) * 3, int(l_y) * 3, 0)
    r_x, r_y = simulation.get_position_of_node(train)
    network.set_position(train, int(r_x) * 3, int(r_y) * 3, 0)


try:
    e().after(2).execute(lambda: sim.start(after_sumo_simulation_step)).start_on_simulation_start()
    e().after(5).execute(lambda: swtch.execute_command("java FileServer", True)).start_on_simulation_start()
    e().after(10).execute(lambda: train.execute_command("java FileClient", True)).start_on_simulation_start()

    ns.core.Simulator.Stop(ns.core.Seconds(6000))
    print("Start Simulation")
    ns.core.Simulator.Run(signal_check_frequency=-1)
    print("Simulation stopped")
except:
    print("Unexpected error:", sys.exc_info())
    pass

print("Start cleanup")
ns.core.Simulator.Destroy()
sim.destroy()
swtch.destroy()
train.destroy()
print("Clean Up Completed")