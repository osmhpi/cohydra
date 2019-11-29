from .simulation import Simulation

class Scenario:

    def __init__(self, netanim_node_size=4):
        self.networks = set()
        self.workflows = set()
        self.simulation = None
        self.netanim_node_size = netanim_node_size


    def add_network(self, network):
        """Add a network to be simulated.
        """
        self.networks.add(network)

    def workflow(self, func):
        self.workflows.add(func)

    def __enter__(self):
        self.simulation = Simulation(self)
        return self.simulation

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.simulation.teardown(raise_on_fail=exc_type is None)
