from __future__ import print_function
from netsimbridge.WifiNetwork import WifiNetwork
from netsimbridge import Simulation
from hostcomponents import Preparation
from nodes.LXDNode import LXDNode
from events.Event import e
import sys

Simulation.prepare_simulation()
Preparation.do_not_filter_bridge_traffic()

node1 = LXDNode("node1", "railToX")
node1.create()
node1.start()

node2 = LXDNode("node2", "railToX")
node2.create()
node2.start()

network = WifiNetwork("net1", tx_power=18)
network.set_delay(4.260/2)
network.add_node(node1, "192.168.2.151", "24", connect_on_create=True)
network.add_node(node2, "192.168.2.152", "24", connect_on_create=True)
network.create()


def offer_user_input():
    for i in range(0, 100):
        new_x = int(input("New x value: "))
        node2.set_position(int(new_x), 0, 0)
        print("Node2 position is now: " + str(node2.position))


e().after(1).execute(offer_user_input).start_on_simulation_start()

try:
    Simulation.start_simulation()
except:
    print("Unexpected error:", sys.exc_info())

print("Start cleanup")
Simulation.destroy_simulation()
node1.destroy()
node2.destroy()
print("Clean Up Completed")
