from __future__ import print_function
from netsimbridge.WifiNetwork import WifiNetwork
from nodes.LXDNode import LXDNode
from events.Event import e
from simulations.SumoSimulation import SumoSimulation
from hostcomponents import Preparation
from netsimbridge import Simulation
import sys

Simulation.prepare_simulation()
Preparation.do_not_filter_bridge_traffic()

swtch = LXDNode("swtch", "railToX")
swtch.create()

train = LXDNode("train", "railToX")
# train = ExternalNetwork("train", "enp0s10")
train.create()

swtch.start()
train.start()
train.set_position(1000, 0, 0)

network = WifiNetwork("net1")
network.set_delay(0)
network.add_node(swtch, "192.168.2.150", "24", connect_on_create=True)
network.add_node(train, "192.168.2.152", "24", connect_on_create=True, bridge_connect=True, bridge_connect_ip="192.168.2.153", bridge_connect_mask="255.255.255.0")
network.create()

sim = SumoSimulation("/home/arne/source/sumo/bin/sumo-gui",
                     "/home/arne/Masterarbeit/sumo-scenarios/scenario4/scenario.sumocfg")
sim.add_node_to_mapping(swtch, "n0", "junction")
sim.add_node_to_mapping(train, "train")


def after_sumo_simulation_step(simulation, traci):
    print("Distance: "+str(simulation.get_distance_between_nodes(swtch, train))+"\n")


try:
    e().after(2).execute(lambda: sim.start(after_sumo_simulation_step)).start_on_simulation_start()
    e().after(5).execute(lambda: swtch.execute_command("java FileServer", True)).start_on_simulation_start()
    e().after(6).execute(lambda: train.execute_command("java FileClient", True)).start_on_simulation_start()
    Simulation.start_simulation()
except:
    print("Unexpected error:", sys.exc_info())
    pass

print("Start cleanup")
Simulation.destroy_simulation()
sim.destroy()
swtch.destroy()
train.destroy()
print("Clean Up Completed")
