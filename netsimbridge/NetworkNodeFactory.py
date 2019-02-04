from ns.network import Node
import ns.tap_bridge

class NetworkNodeFactory:

    @staticmethod
    def get_tuntap_node(tuntapdevice):
        tapbridge = ns.tap_bridge.TapBridgeHelper()
        tapbridge.SetAttribute("Mode", ns.core.StringValue("UseLocal"))
        tapbridge.SetAttribute("DeviceName", ns.core.StringValue(tuntapdevice.name))

        node = Node()
        tapbridge.Install(node, devices.Get(0))



