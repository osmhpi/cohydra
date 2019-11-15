import argparse
import os
import shutil
import subprocess
import sys
import yaml

class Simulation:

    def __init__(self, arguments):
        self.arguments = arguments
        self.ns3_home_dir = os.getenv('NS3_HOME', None)
        if self.ns3_home_dir is None:
            print('Please set the "NS3_HOME" environment variable containing the ns3-sources and waf!',
                  file=sys.stderr)
            exit(-1)
        self.service_names = []
        if self.__setup() != 0:
            print('There was an error setting up iptables for the simulation. Exiting!', file=sys.stderr)
            exit(-1)

    def __setup(self):
        with open(self.arguments.compose_file, 'r') as compose:
            config = yaml.load(compose, Loader=yaml.SafeLoader)
            self.service_names = list(config['services'].keys())
        return_code = subprocess.call("sudo net/fix-iptables.sh", shell=True, stdout=subprocess.PIPE)
        return return_code

    def __build_containers(self):
        print('- Building containers:')
        return_code = subprocess.call(f"docker-compose -f {self.arguments.compose_file} build", shell=True)
        if return_code != 0:
            print('There was an error building the docker containers. Exiting!', file=sys.stderr)
            exit(-1)

    def __copy_build_ns3_config(self):
        print('- Copying NS-3 configuration:')
        try:
            shutil.copy('ns3_configs/tap-star-virtual-machine.cc', 
                        f'{self.ns3_home_dir}/scratch/tap-docker.cc')
        except IOError:
            print('There was an error copying the NS3 configuration. Exiting!', file=sys.stderr)
            exit(-1)

        print('- Building NS-3 (if not already done):')
        return_code = subprocess.call(f'cd {self.ns3_home_dir} && ./waf build -d optimized --disable-examples',
                                      shell=True)
        if return_code != 0:
            print('There was an error building the NS-3 configuration. Exiting!', file=sys.stderr)
            exit(-1)


    def prepare(self):
        """Prepare the simulation.
        """
        print('--------------------------------------------------')
        print('Preparing simulation:')
        self.__build_containers()
        self.__copy_build_ns3_config()

# if __name__ == "__main__":
#     PARSER = argparse.ArgumentParser(description='Parsing parameters for ns-3 simulation')
#     PARSER.add_argument('-nn', '--num-nodes', metavar='N',
#                         type=int, help='The number of nodes to simulate.', required=True)
#     PARSER.add_argument('-compose-file', default='docker-compose.yml', dest='compose_file',
#                         help='The docker compose file to use for the containers.')
#     PARSER.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
#     ARGS = PARSER.parse_args()
#     SIM = Simulation(ARGS)
#     SIM.prepare()
