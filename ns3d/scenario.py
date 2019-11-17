from .simulation import Simulation

class Scenario:

    def __init__(self):
        self.networks = set()
        self.simulation = None


    def add_network(self, network):
        """Add a network to be simulated.
        """
        self.networks.add(network)

    def __enter__(self):
        self.simulation = Simulation(self)
        return self.simulation

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.simulation.teardown(raise_on_fail=exc_type is None)
