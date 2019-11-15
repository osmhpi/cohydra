import os
import subprocess
import sys
import logging
from ns import core

class Simulation:

    def __init__(self, scenario):
        self.ns3_home_dir = os.getenv('NS3_HOME', None)
        if self.ns3_home_dir is None:
            print('Please set the "NS3_HOME" environment variable containing the ns3-sources and waf!',
                  file=sys.stderr)
            exit(-1)
        if self.__setup() != 0:
            print('There was an error setting up iptables for the simulation. Exiting!', file=sys.stderr)
            exit(-1)

        self.scenario = scenario

    def __setup(self):
        return_code = subprocess.call("sudo net/fix-iptables.sh", shell=True, stdout=subprocess.PIPE)
        return return_code

    def prepare(self):
        """Prepares the simulation by building docker containers.
        """
        logging.info('Preparing simulation')

        # This needs to be set to real time, to let the containers speek.
        core.GlobalValue.Bind("SimulatorImplementationType", core.StringValue("ns3::RealtimeSimulatorImpl"))
        core.GlobalValue.Bind("ChecksumEnabled", core.BooleanValue(True))

        for network in self.scenario.networks:
            network.prepare()

    def simulate(self, time):
        """Simulate the network

        :param float time: The simulation timeout in seconds.
        """
        logging.info('Simulating for %.4fs', time)
        core.Simulator.Stop(core.Seconds(time))
        core.Simulator.Run()
        core.Simulator.Destroy()

    def teardown(self):
        """Tear down the simulation.
        This also stops and destroys docker containers.
        """
        for network in self.scenario.networks:
            network.teardown()
  