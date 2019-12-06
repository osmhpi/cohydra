import logging
import os
import threading

from datetime import datetime
from ns import core, internet, netanim
from pyroute2 import IPRoute

import docker

from .util import once
from .workflow import Workflow

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
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.log_directory = os.path.join(os.getcwd(), 'simulation-logs', date)
        os.makedirs(self.log_directory, exist_ok=True)

        self.docker_client = docker.DockerClient()

        # Saves IP -> hostname.
        self.hosts = None

        animation_file = os.path.join(self.log_directory, "netanim.xml")
        self.animation_interface = netanim.AnimationInterface(animation_file)

    @classmethod
    @once
    def __setup(cls):
        bridgedir = '/proc/sys/net/bridge/'
        if not os.path.exists(bridgedir):
            return
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

        # Add host to hostsfile.
        ipr = IPRoute()
        host_ip = ipr.get_addr(label='docker0')[0].get_attr('IFA_ADDRESS')
        self.hosts = [f'host:{host_ip}']

        # Try to add influxdb to hosts file (if container is running).
        try:
            influxdb_container = self.docker_client.containers.get('ns3-influxdb')
            influxdb_ip = influxdb_container.attrs["NetworkSettings"]["IPAddress"]
            if influxdb_ip is not None:
                self.hosts.append(f'influxdb:{influxdb_ip}')
        except docker.errors.NotFound:
            pass

        for network in self.scenario.networks:
            for channel in network.channels:
                host_list = map(lambda kv: (f'{kv[0].name}:{kv[1]}'), channel.ip_map.items())
                self.hosts.extend(host_list)

        network_index = 0
        for network in self.scenario.networks:
            network.prepare(self, network_index)
            network_index += 1

        routing_helper = internet.Ipv4GlobalRoutingHelper
        routing_helper.PopulateRoutingTables()

    def simulate(self, simluation_time=None):
        """Simulate the network

        :param float simluation_time: The simulation timeout in seconds.
        """
        self.prepare()
        self.animation_interface.EnablePacketMetadata(True)

        started = threading.Semaphore(0)

        core.Simulator.Schedule(core.Seconds(0), started.release)

        if simluation_time is not None:
            logger.info('Simulating for %.4fs', simluation_time)
        else:
            logger.info('Simulating until process gets stopped')

        def run_simulation():
            if simluation_time is not None:
                core.Simulator.Stop(core.Seconds(simluation_time))
            core.Simulator.Run()
            core.Simulator.Destroy()

        thread = threading.Thread(target=run_simulation)

        try:
            thread.start()
            started.acquire()

            workflow = Workflow()
            self.add_teardown(workflow.stop)

            for task in self.scenario.workflows:
                workflow.start(task)

            thread.join()
        finally:
            core.Simulator.Stop()

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
