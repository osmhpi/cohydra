import os, sys
import time
from math import sqrt

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
        self.steps = 1000
        self.node_mapping = {}

    def start(self, after_simulation_step, steplength=1, steps=1000):
        self.steps = steps
        traci.start([self.binary_path, "--step-length", str(steplength), "-c", self.config_path])

        step_counter = 0
        while step_counter < self.steps:
            traci.simulationStep()

            # Update positions:
            for node in self.node_mapping:
                x, y, z = self.get_position_of_node(node)
                node.set_position(x, y, z)

            after_simulation_step(self, traci)

            step_counter = step_counter + 1
            time.sleep(traci.simulation.getDeltaT())

        traci.close()

    def add_node_to_mapping(self, node, sumo_vehicle_id, obj_type="vehicle"):
        self.node_mapping[node] = (sumo_vehicle_id, obj_type)

    def get_position_of_node(self, node):
        if node not in self.node_mapping:
            print("Unknown node "+str(node.name))
        else:
            if self.node_mapping[node][1] == "person":
                return traci.person.getPosition3D(self.node_mapping[node][0])
            elif self.node_mapping[node][1] == "vehicle":
                return traci.vehicle.getPosition3D(self.node_mapping[node][0])
            elif self.node_mapping[node][1] == "junction":
                # Junction has no support for 3D positions
                x, y = traci.junction.getPosition(self.node_mapping[node][0])
                return x, y, 0.0
            else:
                print("Unknown type " + str(self.node_mapping[node][1]))

    def get_distance_between_nodes(self, node1, node2):
        x1, y1, z1 = self.get_position_of_node(node1)
        x2, y2, z2 = self.get_position_of_node(node2)
        return sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)

    def destroy(self):
        traci.close()
