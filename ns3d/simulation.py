import logging
import os

from ns import core, internet

from .util import once

logger = logging.getLogger(__name__)

# This needs to be set to real time, to let the containers speek.
core.GlobalValue.Bind("SimulatorImplementationType", core.StringValue("ns3::RealtimeSimulatorImpl"))
core.GlobalValue.Bind("ChecksumEnabled", core.BooleanValue(True))
# core.LogComponentEnableAll(core.LOG_LOGIC)
# core.LogComponentEnable('TapBridge', core.LOG_DEBUG)
# core.LogComponentEnable('TapBridge', core.LOG_WARN)

class Simulation:

    def __init__(self, scenario):
        self.__setup()

        self.scenario = scenario
        self.teardowns = list()

        # Saves IP -> hostname.
        self.hosts = None

    @classmethod
    @once
    def __setup(cls):
        bridgedir = '/proc/sys/net/bridge/'
        for filename in os.listdir(bridgedir):
            if filename.startswith('bridge-nf-'):
                logger.debug('set %s = 0', filename)
                with open(bridgedir + filename, 'w') as file:
                    file.write('0')

    @once
    def prepare(self):
        """Prepares the simulation by building docker containers.
        """
        logger.info('Preparing simulation')

        self.hosts = list()

        for network in self.scenario.networks:
            for channel in network.channels:
                host_list = map(lambda kv: (f'{kv[0].name}:{kv[1]}'), channel.ip_map.items())
                self.hosts.extend(host_list)

        for network in self.scenario.networks:
            network.prepare(self)

        routing_helper = internet.Ipv4GlobalRoutingHelper
        routing_helper.PopulateRoutingTables()

    def simulate(self, time=None):
        """Simulate the network

        :param float time: The simulation timeout in seconds.
        """
        self.prepare()

        if time is not None:
            logger.info('Simulating for %.4fs', time)
            core.Simulator.Stop(core.Seconds(time))
        else:
            logger.info('Simulating until process gets stopped')
        core.Simulator.Run()
        core.Simulator.Destroy()

    def teardown(self, raise_on_fail=True):
        """Tear down the simulation.
        This also stops and destroys docker containers.
        """
        logger.info("Tearing down the simulation (%d teardowns)", len(self.teardowns))

        fails = 0
        while self.teardowns:
            teardown = self.teardowns.pop()
            logger.debug("Running teardown %s (%d teardowns left)", teardown.__name__, len(self.teardowns))

            try:
                teardown()
            except Exception as err: # pylint: disable=broad-except
                logger.error("Failed to run teardown %s: %s", teardown.__name__, err)
                fails += 1

        if fails != 0:
            if raise_on_fail:
                raise Exception(f"Teardown failed: {fails} teardowns failed")
            logger.warning("Teardown failed: %d teardowns failed", fails)
        else:
            logger.info("Teardown successful")

    def add_teardown(self, teardown, name=None):
        """Add a teardown function.
        This function is added to the teardown stack and will be called on teardown.

        :param function teardown: The teardown function.
        :param str name: An optional name to override the name of the teardown function.
        """
        if name is not None:
            teardown.__name__ = name
        logger.debug("Added teardown %s", teardown.__name__)
        self.teardowns.append(teardown)
