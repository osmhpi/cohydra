from __future__ import print_function

from netsimbridge.CSMANetwork import CSMANetwork
from netsimbridge import Simulation
from nodes.LXDNode import LXDNode
from nodes.InterfaceNode import InterfaceNode
from hostcomponents import Preparation
from events.Event import e
import traceback
import sys

Preparation.do_not_filter_bridge_traffic()
Simulation.prepare_simulation()

conleft = LXDNode("db", "iot-postgres")
conleft.create()
conleft.start()
externalnetwork1 = InterfaceNode("enet1", "enx00e04c5804b9")

network = CSMANetwork("net1")
network.set_delay(100)
network.set_data_rate("100Mbps")

try:
    network.add_node(conleft, "192.168.2.70", "255.255.255.0", bridge_connect=True, bridge_connect_ip="192.168.2.252",
                     bridge_connect_mask="255.255.255.0", connect_on_create=True)
    network.add_node(externalnetwork1, bridge_connect=True, bridge_connect_ip="192.168.2.253",
                     bridge_connect_mask="255.255.255.0", connect_on_create=True)
    network.create()

    e().after(120).execute(lambda: network.disconnect_node(externalnetwork1))\
       .after(120).execute(lambda: network.connect_node(externalnetwork1)).start_on_simulation_start()
    e().after(30).execute(lambda: externalnetwork1.execute_command("192.168.2.12", "pi", "pi",
                                                                   "service iot-save start", sudo=True))\
       .start_on_simulation_start()
    Simulation.start_simulation()
except Exception as e:
    print("Unexpected error:")
    print(traceback.format_exc())
finally:
    print("Start cleanup")
    Simulation.destroy_simulation()
    network.destroy()
    conleft.destroy()

    externalnetwork1.execute_command("192.168.2.12", "pi", "pi", "service iot-save stop", sudo=True)
    externalnetwork1.destroy()
    print("Clean Up Completed")
    sys.exit()
