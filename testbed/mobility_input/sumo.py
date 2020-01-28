"""SUMO co-simulation."""

import logging
import os
import sys
import threading
import time

from math import hypot

if 'SUMO_HOME' in os.environ:
    TOOLS = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(TOOLS)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

from .mobility_input import MobilityInput

logger = logging.getLogger(__name__)

class SUMOMobilityInput(MobilityInput):
    """SUMOMobilityInput is an interface to the SUMO simulation environment."""

    def __init__(self, binary_path, config_path, name="SUMO External Simulation", steps=1000):
        """Create a new SUMOMobilityInput.

        name : str
            The name of the MobilityInput.
        binary_path : str
            The path to the `sumo` binary.
        config_path : str
            The path to the simulation configuration (.cfg).
        """
        super().__init__(name)
        ## The path to the SUMO binary / server.
        self.binary_path = binary_path
        ## The path to the simulation scenarion configuration.
        self.config_path = config_path
        ## The number of steps to simulate.
        self.steps = steps

        self.step_counter = 0

    def prepare(self, simulation):
        """Start SUMO server."""
        logger.info('Starting SUMO for %s.', self.name)
        traci.start([self.binary_path, "-c", self.config_path])
        self.step_counter = 0

    def start(self):
        """Start a thread stepping through the sumo simulation."""
        logger.info('Starting SUMO stepping for %s.', self.name)
        def run_sumo():
            try:
                while self.step_counter < self.steps:
                    traci.simulationStep()

                    # Update positions:
                    for node in self.node_mapping:
                        x, y = self.__get_position_of_node(node)
                        node.set_position(x, y, 0)

                    self.step_counter = self.step_counter + 1
                    time.sleep(traci.simulation.getDeltaT())
            except traci.exceptions.FatalTraCIError:
                logger.warning('Something went wrong with SUMO for %s. Maybe the connection was closed.', self.name)

        thread = threading.Thread(target=run_sumo)
        thread.start()

    def add_node_to_mapping(self, node, sumo_vehicle_id, obj_type="vehicle"):
        self.node_mapping[node] = (sumo_vehicle_id, obj_type)

    def __get_position_of_node(self, node):
        if node not in self.node_mapping:
            print("Unknown node "+str(node.name))
        else:
            if self.node_mapping[node][1] == "person":
                return traci.person.getPosition(self.node_mapping[node][0])
            elif self.node_mapping[node][1] == "vehicle":
                return traci.vehicle.getPosition(self.node_mapping[node][0])
            elif self.node_mapping[node][1] == "junction":
                return traci.junction.getPosition(self.node_mapping[node][0])
            else:
                print("Unknown type " + str(self.node_mapping[node][1]))

    def destroy(self):
        """Stop SUMO."""
        logger.info('Trying to close SUMO for %s.', self.name)
        # Trigger abort of loop.
        self.step_counter = self.steps
        traci.close()
