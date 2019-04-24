from __future__ import print_function

from netsimbridge.CSMANetwork import CSMANetwork
from lxdcontainer.LXDContainer import LXDContainer
from externalnetwork.ExternalNetwork import ExternalNetwork
import ns.core
import traceback
from events.Event import e
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


conleft = LXDContainer("db", "iot-postgres")
conleft.create()
conleft.start()
externalnetwork1 = ExternalNetwork("enet1", "enx00e04c5804b9")

network = CSMANetwork("net1")
network.set_delay(100)
network.set_data_rate("100Mbps")

try:
    prepare_scenario()

    ns.core.GlobalValue.Bind("SimulatorImplementationType", ns.core.StringValue("ns3::RealtimeSimulatorImpl"))
    ns.core.GlobalValue.Bind("ChecksumEnabled", ns.core.BooleanValue("true"))

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
    ns.core.Simulator.Stop(ns.core.Seconds(6000))
    print("Start Simulation")
    ns.core.Simulator.Run(signal_check_frequency=-1)
    print("Simulation stopped")
except Exception as e:
    print("Unexpected error:")
    print(traceback.format_exc())
finally:
    print("Start cleanup")
    ns.core.Simulator.Destroy()
    network.destroy()
    conleft.destroy()

    externalnetwork1.execute_command("192.168.2.12", "pi", "pi", "service iot-save stop", sudo=True)
    externalnetwork1.destroy()
    print("Clean Up Completed")
    sys.exit()
