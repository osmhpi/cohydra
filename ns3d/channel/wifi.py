import ipaddress
import logging
import os

from ns import core, internet, network as ns_net, wifi

from .channel import Channel
from ..interface import Interface

logger = logging.getLogger(__name__)

class WifiChannel(Channel):
    """!A WifiChannel is a physical (but of course wireless) connection
        between two or more wireless devices.
    """

    def __init__(self, network, nodes, frequency=5510, channel_width=40, antennas=2, tx_power=20.0):
        """! @inheritDocs

        @param frequency The frequency of the wireless channel in MHz.
        @param channel_width The width of the channel in MHz.
            Valid values are `5`, `10`, `20`, `22`, `40`, `80`, `160`.
        @param antennas The number of antennas to use.
        @param tx_power The sending power in dBm.
        """
        super().__init__(network, nodes)

        ## The channel's frequency.
        #
        # This could collide with other WIFI channels.
        self.frequency = frequency
        ## The width of the channel in MHz.
        self.channel_width = channel_width
        ## The number of antennas to use.
        self.antennas = antennas
        ## The sending power in dBm.
        self.tx_power = tx_power

        logger.debug("Setting up physical layer of Wifi.")
        self.wifi_phy_helper = wifi.YansWifiPhyHelper.Default()
        self.wifi_phy_helper.Set("Frequency", core.UintegerValue(self.frequency))
        self.wifi_phy_helper.Set("ChannelWidth", core.UintegerValue(self.channel_width))
        self.wifi_phy_helper.Set("Antennas", core.UintegerValue(self.antennas))
        self.wifi_phy_helper.Set("TxPowerStart", core.DoubleValue(self.tx_power))
        self.wifi_phy_helper.Set("TxPowerEnd", core.DoubleValue(self.tx_power))

        # Enable monitoring of radio headers.
        self.wifi_phy_helper.SetPcapDataLinkType(wifi.WifiPhyHelper.DLT_IEEE802_11_RADIO)

        wifi_channel_helper = wifi.YansWifiChannelHelper()
        wifi_channel_helper.SetPropagationDelay("ns3::ConstantSpeedPropagationDelayModel")
        # wifi_channel_helper.AddPropagationLoss("ns3::LogDistancePropagationLossModel")
        wifi_channel_helper.AddPropagationLoss("ns3::RangePropagationLossModel")

        self.wifi_phy_helper.SetChannel(wifi_channel_helper.Create())

        ## Helper for creating the Wifi channel
        self.wifi = wifi.WifiHelper()
        data_rate = "ErpOfdmRate54Mbps"
        self.wifi.SetRemoteStationManager("ns3::ConstantRateWifiManager",
                                          "DataMode", core.StringValue(data_rate),
                                          "ControlMode", core.StringValue(data_rate))
        # self.wifi.SetRemoteStationManager("ns3::IdealWifiManager")
        self.wifi.SetStandard(wifi.WIFI_PHY_STANDARD_80211g)

        wifi_mac_helper = wifi.WifiMacHelper()

        # Adhoc network between multiple nodes (no access point).
        wifi_mac_helper.SetType("ns3::AdhocWifiMac")

        # Install on all connected nodes.
        logger.debug("Installing the Wifi channel to %d nodes.", len(nodes))

        ## All ns-3 devices on this channel.
        self.devices_container = self.wifi.Install(self.wifi_phy_helper, wifi_mac_helper, self.ns3_nodes_container)

        logger.info('Setting IP addresses on nodes.')
        stack_helper = internet.InternetStackHelper()

        for i, node in enumerate(nodes):
            ns3_device = self.devices_container.Get(i)

            address = None
            if node.wants_ip_stack():
                if node.ns3_node.GetObject(internet.Ipv4.GetTypeId()) is None:
                    logger.info('Installing IP stack on %s', node.name)
                    stack_helper.Install(node.ns3_node)
            device_container = ns_net.NetDeviceContainer(ns3_device)
            ip_address = self.network.address_helper.Assign(device_container).GetAddress(0)
            netmask = network.network.prefixlen
            address = ipaddress.ip_interface(f'{ip_address}/{netmask}')

            interface = Interface(node=node, ns3_device=ns3_device, address=address)
            node.add_interface(interface)
            self.interfaces.append(interface)


    def prepare(self, simulation):
        """! Prepare the channel enabling logging."""
        for interface in self.interfaces:
            pcap_log_path = os.path.join(simulation.log_directory, interface.pcap_file_name)
            self.wifi_phy_helper.EnablePcap(pcap_log_path, interface.ns3_device, True, True)
