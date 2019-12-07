import logging

from .simulation import Simulation
from .context import Context, SimpleContext

logger = logging.getLogger(__name__)

class Scenario:

    def __init__(self, netanim_node_size=4):
        self.networks = set()
        self.workflows = set()
        self.simulation = None
        self.context = None
        self.netanim_node_size = netanim_node_size


    def add_network(self, network):
        """Add a network to be simulated.
        """
        self.networks.add(network)

    def channels(self):
        for network in self.networks:
            for channel in network.channels:
                yield channel

    def nodes(self):
        seen = set()
        for channel in self.channels():
            for interface in channel.interfaces:
                node = interface.node
                if node not in seen:
                    seen.add(node)
                    yield node

    def workflow(self, func):
        self.workflows.add(func)

    def __enter__(self):
        self.simulation = Simulation(self)
        if Context.current() is None:
            logger.warning('No context found, using SimpleContext as a fallback')
            self.context = SimpleContext()
            self.context.__enter__()
        return self.simulation

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.context is not None:
            self.context.__exit__(exc_type, exc_value, exc_traceback)
            self.context = None
