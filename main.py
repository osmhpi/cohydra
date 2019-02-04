from netsimbridge.CSMANetwork import CSMANetwork
from lxdcontainer.LXDContainer import LXDContainer
import ns.core
import sys

ns.core.GlobalValue.Bind("SimulatorImplementationType", ns.core.StringValue("ns3::RealtimeSimulatorImpl"))
ns.core.GlobalValue.Bind("ChecksumEnabled", ns.core.BooleanValue("true"))

conleft = LXDContainer("con-left", "ubuntu:16.04")
conleft.create()

conright = LXDContainer("con-right", "ubuntu:16.04")
conright.create()


conleft.start()
conright.start()

try:
    print("a1")
    network = CSMANetwork(2, 100, 2000)
    print("a2")
    network.add_node(conleft, "10.199.198.2", "24", "10.199.198.255", "10.199.198.1")
    print("a3")
    network.add_node(conright, "10.199.199.2", "24", "10.199.199.255", "10.199.199.1")
    print("a4")
    #network.set_delay(2000)

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
print("Clean Up Completed")