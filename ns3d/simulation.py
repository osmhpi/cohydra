import logging
import os
import threading

from datetime import datetime
from ns import core, internet, netanim
from pyroute2 import IPRoute

import docker

from .util import once
from .context import defer
from .workflow import Workflow

logger = logging.getLogger(__name__)

# This needs to be set to real time, to let the containers speek.
core.GlobalValue.Bind("SimulatorImplementationType", core.StringValue("ns3::RealtimeSimulatorImpl"))
core.GlobalValue.Bind("ChecksumEnabled", core.BooleanValue(True))
# core.LogComponentEnableAll(core.LOG_LOGIC)
# core.LogComponentEnable('TapBridge', core.LOG_DEBUG)
# core.LogComponentEnable('TapBridge', core.LOG_WARN)
# core.LogComponentEnable('MacLow', core.LOG_DEBUG)
# core.LogComponentEnable('Txop', core.LOG_DEBUG)

class Simulation:
    """! @brief The simulation runs ns-3.
    The simulation is described by a scenario which also prepares the simulation.
    It also takes care of preparing networks and nodes.
    """
    def __init__(self, scenario):
        """! Create a new simulation.

        @param scenario The scenario to run the simulation with.
        """
        self.__setup()

        ## The scenario describing the simulation.
        self.scenario = scenario
        ## The teardowns being run when the simulation finishes.
        self.teardowns = list()
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        ## The directory where all log files are stored.
        self.log_directory = os.path.join(os.getcwd(), 'simulation-logs', date)
        os.makedirs(self.log_directory, exist_ok=True)

        ## A docker runtime client for checking whether there is an
        ## influxdb running for monitoring purposes.
        self.docker_client = docker.DockerClient()

        # Saves IP -> hostname.
        ## All hosts of the simulation for mapping in nodes.
        ##
        ## This can be used to modify the hosts file.
        self.hosts = None
        ## NetAnim interface.
        self.animation_interface = None
        ## Indicates whether the simulation is started.
        self.started = False

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
        """! Prepares the simulation by setting up networks and nodes.

        Iterates over all networks of the scenario and preparing them.
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

        for channel in self.scenario.channels():
            for interface in channel.interfaces:
                if interface.address is not None:
                    self.hosts.append(f'{interface.node.name}:{interface.address.ip}')

        for (i, network) in enumerate(self.scenario.networks):
            network.prepare(self, i)

        animation_file = os.path.join(self.log_directory, "netanim.xml")
        self.animation_interface = netanim.AnimationInterface(animation_file)
        self.animation_interface.EnablePacketMetadata(True)

        node_size = self.scenario.netanim_node_size
        for node in self.scenario.nodes():
            self.animation_interface.UpdateNodeDescription(node.ns3_node, node.name)
            if node.color:
                self.animation_interface.UpdateNodeColor(node.ns3_node, *node.color)
            self.animation_interface.UpdateNodeSize(node.ns3_node.GetId(), node_size, node_size)
            node.prepare(self)

        routing_helper = internet.Ipv4GlobalRoutingHelper
        routing_helper.PopulateRoutingTables()

    def simulate(self, simluation_time=None):
        """! Simulate the network

        @param simluation_time The simulation timeout in seconds.
        """
        if self.started:
            raise Exception('The simulation was already started')
        self.started = True

        self.prepare()

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
            defer('stop workflows', workflow.stop)

            for task in self.scenario.workflows:
                workflow.start(task)

            thread.join()
        finally:
            core.Simulator.Stop()
