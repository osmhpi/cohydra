from __future__ import print_function

from netsimbridge.WifiNetwork import WifiNetwork
from netsimbridge import Simulation
from nodes.LXDNode import LXDNode
from events.Event import e
from hostcomponents import Preparation
import sys
# import ns.core

# ns.core.LogComponentEnable("TapBridgeHelper", ns.core.LOG_LEVEL_INFO)
# ns.core.LogComponentEnable("TapBridge", ns.core.LOG_LEVEL_INFO)
# ns.core.LogComponentEnable("NetDevice", ns.core.LOG_LEVEL_INFO)
# ns.core.LogComponentEnable("Object", ns.core.LOG_LEVEL_INFO)
# ns.core.LogComponentEnable("Config", ns.core.LOG_LEVEL_ALL)

Preparation.do_not_filter_bridge_traffic()
Simulation.prepare_simulation()

conleft = LXDNode("left", "java")  # ubuntu:16.04
conleft.create()

conright = LXDNode("right", "java")  # ubuntu:16.04
conright.create()

conleft.start()
conright.start()

network = WifiNetwork("net1")
network.add_node(conleft, "10.1.1.2", "24", connect_on_create=True)
network.add_node(conright, "10.1.1.3", "24", connect_on_create=True)
network.create()

network2 = WifiNetwork("net2")
network2.add_node(conleft, "192.168.2.100", "24", connect_on_create=True)
network2.add_node(conright, "192.168.2.101", "24", connect_on_create=True)
network2.create()

try:
    e().after(30).execute(lambda: network.disconnect_node(conright)).start_on_simulation_start()
    Simulation.start_simulation()
except:
    print("Unexpected error:", sys.exc_info())
    pass

print("Start cleanup")
Simulation.destroy_simulation()
conleft.destroy()
conright.destroy()
print("Clean Up Completed")