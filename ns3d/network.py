class Network:
    """
    A network connects many nodes together and assigns IP addresses.
    It can be compared to a subnet or so.
    """

    def __init__(self):
        self.nodes = list()
    
    def prepare(self):
        """Prepares the network by building the docker containers.
        """
        for node in self.nodes:
            node.prepare()