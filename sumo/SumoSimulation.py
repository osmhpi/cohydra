import os, sys
import time
from math import hypot

if 'SUMO_HOME' in os.environ:
 tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
 sys.path.append(tools)
else:
 sys.exit("please declare environment variable 'SUMO_HOME'")

import traci


class SumoSimulation(object):

    def __init__(self, binary_path, config_path):
        self.binary_path = binary_path
        self.config_path = config_path
        self.delay = 100
        self.steps = 1000
        self.node_mapping = {}

    def set_delay(self, delay):
        self.delay = delay

    def start(self, after_simulation_step, steps=1000):
        self.steps = steps
        traci.start([self.binary_path, "-c", self.config_path])

        step_counter = 0
        while step_counter < self.steps:
            traci.simulationStep()
            after_simulation_step(self, traci)
            step_counter = step_counter + 1
            time.sleep(self.delay/1000)

        traci.close()

    def add_node_to_mapping(self, node, sumo_vehicle_id):
        self.node_mapping[node.name] = sumo_vehicle_id

    def get_position_of_node(self, node):
        return traci.vehicle.getPosition(self.node_mapping[node.name])

    def get_distance_between_nodes(self, node1, node2):
        x1, y1 = self.get_position_of_node(node1)
        x2, y2 = self.get_position_of_node(node2)
        return hypot(x2 - x1, y2 - y1)
