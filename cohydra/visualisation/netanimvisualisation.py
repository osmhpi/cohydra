"""NetAnim Visualisation using the NetAnim format."""

from .visualisation import Visualisation

from ns import netanim

class NetAnimVisualisation(Visualisation):
    """The NetAnimVisualisation class produces a netanim.xml file which
    contains visualistion details in the NetAnim format.

    To create a NetAnim visualisation, use:

    .. code-block:: python

        from cohydra.visualisation import Visualisation
        from cohydra.visualisation.netanimvisualisation import NetAnimVisualisation
        Visualisation.set_visualisation(NetAnimVisualisation())
    """

    def __init__(self):
        super().__init__()
        animation_file = os.path.join(self.log_directory, "netanim.xml")
        self.animation_interface = netanim.AnimationInterface(animation_file)
        self.animation_interface.EnablePacketMetadata(True)

    def prepare_node(self, node):
        self.animation_interface.UpdateNodeDescription(node.ns3_node, node.name)
        if node.color:
            self.animation_interface.UpdateNodeColor(node.ns3_node, *node.color)
        self.animation_interface.UpdateNodeSize(
            node.ns3_node.GetId(),
            self.node_size,
            self.node_size
        )

    def set_node_position(self, node, x, y, z=0):
        self.animation_interface.SetConstantPosition(node.ns3_node, x, y, z)
