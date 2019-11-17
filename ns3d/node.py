import logging
import time

from ns import core, tap_bridge
from nsenter import Namespace
from pyroute2 import IPRoute, netlink
import docker

class Node:
    """A node is representing a docker container.
    """

    def __init__(self, name, docker_image=None, docker_build_dir=None, dockerfile='Dockerfile'):
        self.name = name
        self.container_name = ''.join(c.lower() for c in self.name if not c.isspace())
        self.docker_image = docker_image
        self.docker_build_dir = docker_build_dir
        self.dockerfile = dockerfile
        self.is_prepared = False
        self.container = None
        self.container_pid = None
        self.interfaces = list()
        self.tap_bridge = None
        if docker_build_dir is None and docker_image is None:
            raise Exception('Please specify Docker image or build directory')

    def __tap_name(self):
        if self.container_name is None:
            raise Exception('Container must be created prior to creating bridges.')
        return f'tap-{self.container_name}'

    def __bridge_name(self):
        if self.container_name is None:
            raise Exception('Container must be created prior to creating bridges.')
        return f'br-{self.container_name}'

    def __external_veth_if_name(self):
        if self.container_name is None:
            raise Exception('Container must be created prior to creating VETH pair.')
        return f'ext-{self.container_name}'

    def __internal_veth_if_name(self):
        return 'eth0'

    def __build_docker_image(self):
        client = docker.from_env()
        if self.docker_image is None:
            logging.info('Building docker image: %s/%s', self.docker_build_dir, self.dockerfile)
            self.docker_image = client.images.build(path=self.docker_build_dir, dockerfile=self.dockerfile)[0].id
        else:
            logging.info('Building docker image: %s', self.docker_image)
            client.images.pull(self.docker_image)

    def __start_docker_container(self):
        logging.info('Starting docker container: %s', self.docker_image)
        client = docker.from_env()
        self.container = client.containers.run(self.docker_image, remove=True, auto_remove=True,
                                               network_mode='none', detach=True, name=self.container_name,
                                               privileged=True)
        low_level_client = docker.APIClient()
        self.container_pid = low_level_client.inspect_container(self.container.id)['State']['Pid']

    def __stop_docker_container(self):
        logging.info('Stopping docker container: %s', self.container.name)
        if self.container is not None:
            self.container.stop(timeout=1)
            self.container = None
            self.container_pid = None

    def __setup_tap_bridge(self, ns3_node, ns3_device, node_ip):
        # Create Bridge
        try:
            ipr = IPRoute()
            ipr.link('add', ifname=self.__bridge_name(), kind='bridge')
            ipr.link('set', ifname=self.__bridge_name(), state='up')
            ipr.link('add', ifname=self.__external_veth_if_name(),
                     peer={
                         "ifname": self.__internal_veth_if_name(),
                         "net_ns_fd": f"/proc/{self.container_pid}/ns/net",
                     },
                     kind='veth')
            ipr.link('set', ifname=self.__external_veth_if_name(),
                     master=ipr.link_lookup(ifname=self.__bridge_name())[0])
            ipr.link('set', ifname=self.__external_veth_if_name(), state='up')
            # Add the tap.
            ipr.link('add', ifname=self.__tap_name(), kind="tuntap", mode="tap")
            ipr.link('set', ifname=self.__tap_name(), state='up')
            ipr.link('set', ifname=self.__tap_name(),
                     master=ipr.link_lookup(ifname=self.__bridge_name())[0])

            self.tap_bridge = tap_bridge.TapBridgeHelper()
            self.tap_bridge.SetAttribute("Mode", core.StringValue("UseBridge"))
            self.tap_bridge.SetAttribute("DeviceName", core.StringValue(self.__tap_name()))
            self.tap_bridge.Install(ns3_node, ns3_device)

        except netlink.exceptions.NetlinkError:
            logging.warning('Failed to setup bridges for: %s', self.name)

        # Get container's namespace and setup interfaces in container.
        with Namespace(self.container_pid, 'net'):
            # This is executed in the container's namespace!
            container_ipr = IPRoute()
            eth0_index = container_ipr.link_lookup(ifname=self.__internal_veth_if_name())[0]
            container_ipr.addr('add', index=eth0_index, address=node_ip, mask=24)
            container_ipr.link('set', index=eth0_index, state='up')

    def __remove_tap_bridge(self):
        ipr = IPRoute()
        ipr.link('delete', ifname=self.__bridge_name())
        ipr.link('delete', ifname=self.__tap_name())
        # VETH pair gets destroyed automatically, when container dies.

    def prepare(self, ns3_node, ns3_device, node_ip):
        """Prepares the node by building the docker container and ?
        """
        if not self.is_prepared:
            logging.info('Preparing node')
            self.__build_docker_image()
            self.__start_docker_container()
            self.__setup_tap_bridge(ns3_node, ns3_device, node_ip)
            self.is_prepared = True
        else:
            logging.info('Node already prepared')


    def teardown(self):
        self.__remove_tap_bridge()
        self.__stop_docker_container()
