import logging

from nsenter import Namespace
from pyroute2 import IPRoute, netlink
from ns import core, network, internet, tap_bridge
import docker

logger = logging.getLogger(__name__)

class Node:
    """A node is representing a docker container.
    """

    def __init__(self, name, docker_image=None, docker_build_dir=None, dockerfile='Dockerfile'):
        self.name = name
        self.container_name = ''.join(c.lower() for c in self.name if not c.isspace())
        self.docker_image = docker_image
        self.docker_build_dir = docker_build_dir
        self.dockerfile = dockerfile

        self.container = None
        self.container_pid = None

        self.interfaces = list()
        self.interface_counter = 0

        self.ns3_node_container = None

        if docker_build_dir is None and docker_image is None:
            raise Exception('Please specify Docker image or build directory')

    def ns3_node(self):
        if self.ns3_node_container is None:
            self.ns3_node_container = network.NodeContainer()
            self.ns3_node_container.Create(1)
        return self.ns3_node_container.Get(0)

    def __tap_name(self):
        if self.container_name is None:
            raise Exception('Container must be created prior to creating bridges.')
        return f'tap-{self.container_name}-{self.interface_counter}'

    def __bridge_name(self):
        if self.container_name is None:
            raise Exception('Container must be created prior to creating bridges.')
        return f'br-{self.container_name}-{self.interface_counter}'

    def __external_veth_if_name(self):
        if self.container_name is None:
            raise Exception('Container must be created prior to creating VETH pair.')
        return f'ext-{self.container_name}-{self.interface_counter}'

    def __internal_veth_if_name(self):
        return f'eth{self.interface_counter}'

    def __build_docker_image(self):
        client = docker.from_env()
        if self.docker_image is None:
            logger.info('Building docker image: %s/%s', self.docker_build_dir, self.dockerfile)
            self.docker_image = client.images.build(path=self.docker_build_dir, dockerfile=self.dockerfile)[0].id
        else:
            logger.info('Building docker image: %s', self.docker_image)
            client.images.pull(self.docker_image)

    def __start_docker_container(self, simulation):
        logger.info('Starting docker container: %s', self.docker_image)
        client = docker.from_env()
        self.container = client.containers.run(self.docker_image, remove=True, auto_remove=True,
                                               network_mode='none', detach=True, name=self.container_name,
                                               privileged=True)
        simulation.add_teardown(self.__stop_docker_container)

        low_level_client = docker.APIClient()
        self.container_pid = low_level_client.inspect_container(self.container.id)['State']['Pid']

    def __stop_docker_container(self):
        if self.container is not None:
            logger.info('Stopping docker container: %s', self.container.name)
            self.container.stop(timeout=1)
            self.container = None
            self.container_pid = None

    def __setup_tap_bridge(self, simulation, ns3_device):
        # Create Bridge
        try:
            ipr = IPRoute()
            bridge_name = self.__bridge_name()
            ipr.link('add', ifname=bridge_name, kind='bridge')
            ipr.link('set', ifname=bridge_name, state='up')
            simulation.add_teardown(lambda: self.__remove_ipr(bridge_name), "remove bridge")

            # Add the tap.
            tap_name = self.__tap_name()
            ipr.link('add', ifname=tap_name, kind="tuntap", mode="tap")
            ipr.link('set', ifname=tap_name, state='up')
            ipr.link('set', ifname=tap_name,
                    master=ipr.link_lookup(ifname=bridge_name)[0])
            simulation.add_teardown(lambda: self.__remove_ipr(tap_name), "remove tap")

            tap = tap_bridge.TapBridgeHelper()
            tap.SetAttribute("Mode", core.StringValue("UseBridge"))
            tap.SetAttribute("DeviceName", core.StringValue(tap_name))
            tap.Install(self.ns3_node(), ns3_device)
        except netlink.exceptions.NetlinkError as err:
            logger.warning('Failed to setup bridge pair for: %s', self.name)
            raise err

    def __setup_veth(self, node_ip):
        # Create VETH pair
        try:
            ipr = IPRoute()
            ipr.link('add', ifname=self.__external_veth_if_name(),
                     peer={
                         "ifname": self.__internal_veth_if_name(),
                         "net_ns_fd": f"/proc/{self.container_pid}/ns/net",
                     },
                     kind='veth')
            ipr.link('set', ifname=self.__external_veth_if_name(),
                     master=ipr.link_lookup(ifname=self.__bridge_name())[0])
            ipr.link('set', ifname=self.__external_veth_if_name(), state='up')
        except netlink.exceptions.NetlinkError as err:
            logger.warning('Failed to setup VETH pair for: %s', self.name)
            raise err

        # Get container's namespace and setup interfaces in container.
        with Namespace(self.container_pid, 'net'):
            # This is executed in the container's namespace!
            container_ipr = IPRoute()
            eth_index = container_ipr.link_lookup(ifname=self.__internal_veth_if_name())[0]
            container_ipr.addr('add', index=eth_index, address=node_ip, mask=24)
            container_ipr.link('set', index=eth_index, state='up')

    def __remove_ipr(self, ifname):
        ipr = IPRoute()
        logger.info('Removing network interface: %s', ifname)
        ipr.link('delete', ifname=ifname)
        # VETH pair gets destroyed automatically, when container dies.

    def prepare(self, simulation, ns3_device, node_ip):
        """Prepares the node by building the docker container and ?
        """
        logging.info('Preparing node %s (having %s)', self.name, node_ip)
        if self.container is None:
            self.__build_docker_image()
            self.__start_docker_container(simulation)
        self.__setup_tap_bridge(simulation, ns3_device)
        self.__setup_veth(node_ip)
        self.interface_counter += 1
