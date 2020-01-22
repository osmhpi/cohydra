import logging

from ns import network as ns_net

logger = logging.getLogger(__name__)

class Channel:
    """! The Channel resembles a physical connection of nodes.

    For CSMA this would be equivalent to one LAN cable.
    All Nodes connected to a channel will be on one collision domain.
    """

    def __init__(self, network, nodes):
        """! Create a new Channel.

        *Warning:* Do not instantiate a channel yourself.
            Use the network's capabilities to link nodes.

        @param network The network this channel belongs to.
        @param nodes The nodes to connect on a physical channel.
        """
        ## The network the channel belongs to.
        self.network = network

        ## All Interfaces (~network cards) on this channel.
        self.interfaces = []

        logger.debug('Creating container with %d nodes', len(nodes))
        ## A container with all ns-3 internal nodes.
        self.ns3_nodes_container = ns_net.NodeContainer()
        for node in nodes:
            self.ns3_nodes_container.Add(node.ns3_node)

    @property
    def nodes(self):
        """! Return all nodes of this channel."""
        logger.warning('Channel.nodes is deprecated. Use ??? instead.')
        return list(map(lambda interface: interface.node, self.interfaces))

    def prepare(self, simulation):
        """! Prepare the channel."""
        raise NotImplementedError
