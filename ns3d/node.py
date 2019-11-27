import asyncio
import logging
import os

from nsenter import Namespace
from pyroute2 import IPRoute, netlink
from ns import core, csma, bridge, network, tap_bridge
import docker

logger = logging.getLogger(__name__)

class Node:
    def __init__(self, name):
        for char in name:
            if not (char.isalnum() or char == '-'):
                raise ValueError('Please only supply alphanumeric names and "-"')
        self.ns3_node_container = None
        self.channels = list()
        self.name = name

        self.ns3_node_container = network.NodeContainer()
        self.ns3_node_container.Create(1)
        core.Names.Add(self.name, self.ns3_node_container.Get(0))

    def ns3_node(self):
        return self.ns3_node_container.Get(0)

    def prepare(self, simulation, ns3_device, node_ip):
        raise NotImplementedError

    def wants_ip_stack(self):
        raise NotImplementedError

    def go_offline(self):
        n_devices = self.ns3_node().GetNDevices()
        for device_index in range(0, n_devices):
            device = self.ns3_node().GetDevice(device_index)
            if isinstance(device, csma.CsmaNetDevice):
                device.SetSendEnable(False)
                device.SetReceiveEnable(False)

    def go_online(self):
        n_devices = self.ns3_node().GetNDevices()
        for device_index in range(0, n_devices):
            device = self.ns3_node().GetDevice(device_index)
            if isinstance(device, csma.CsmaNetDevice):
                device.SetSendEnable(True)
                device.SetReceiveEnable(True)

class BridgeNode(Node):
    """This is representing a bridge between other nodes.
       It acts like a switch.
    """

    def __init__(self, name):
        super().__init__(name)
        bridge_helper = bridge.BridgeHelper()
        self.bridge_device = bridge_helper.Install(self.name, network.NetDeviceContainer()).Get(0)

    def prepare(self, simulation, ns3_device, node_ip):
        if node_ip is not None:
            raise 'Bridges may not have IP addresses.'

        self.bridge_device.AddBridgePort(ns3_device)

    def wants_ip_stack(self):
        return False

def log_to_file(container, log_path):
    with open(log_path, 'wb') as log_file:
        for line in container.logs(stdout=True, follow=True, stream=True):
            log_file.write(line)

class DockerNode(Node):
    """A node is representing a docker container.
    """

    interface_counter = 0

    def __init__(self, name, docker_image=None, docker_build_dir=None, dockerfile='Dockerfile',
                 volumes=None, cpus=0.0, memory=None):
        super().__init__(name)
        self.docker_image = docker_image
        self.docker_build_dir = docker_build_dir
        self.dockerfile = dockerfile
        if volumes is None:
            volumes = {}
        strings_to_volumes = lambda kv: (kv[0], {'bind': kv[1], 'mode': 'rw'} if isinstance(kv[1], str) else kv[1])
        self.volumes = dict(map(strings_to_volumes, volumes.items()))
        self.cpus = cpus
        self.memory = memory

        self.container = None
        self.container_pid = None
        self.network = None

        self.channel_counter = 0

        if docker_build_dir is None and docker_image is None:
            raise Exception('Please specify Docker image or build directory')

    def __image_tag(self):
        return f'ns3-{self.name}'

    def wants_ip_stack(self):
        return True

    def __interface_name(self, prefix):
        return f'{prefix}-ns3-{DockerNode.interface_counter}'

    def __tap_name(self):
        return self.__interface_name('tap')

    def __bridge_name(self):
        return self.__interface_name('br')

    def __external_veth_if_name(self):
        return self.__interface_name('ext')

    def __internal_veth_if_name(self):
        return f'ns3-eth{self.channel_counter}'

    def __build_docker_image(self):
        client = docker.from_env()
        if self.docker_image is None:
            logger.info('Building docker image: %s/%s', self.docker_build_dir, self.dockerfile)
            self.docker_image = client.images.build(path=self.docker_build_dir, dockerfile=self.dockerfile, rm=True)[0]
        else:
            logger.info('Pulling docker image: %s', self.docker_image)
            self.docker_image = client.images.pull(self.docker_image)
        self.docker_image.tag(self.__image_tag())


    def __start_docker_container(self, simulation):
        logger.info('Starting docker container: %s', self.name)
        client = docker.from_env()
        self.container = client.containers.run(self.__image_tag(), remove=True, auto_remove=True,
                                               detach=True, name=self.name,
                                               hostname=self.name, privileged=True, volumes=self.volumes,
                                               nano_cpus=int(self.cpus * 1e9),
                                               mem_limit=0 if self.memory is None else self.memory,
                                               extra_hosts=simulation.hosts, labels={"created-by": "ns-3"})
        simulation.add_teardown(self.__stop_docker_container)

        log_file_path = os.path.join(simulation.log_directory, f'{self.name}.log')
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, log_to_file, self.container, log_file_path)

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
        logger.info('Preparing node %s (having %s)', self.name, node_ip)
        self.__build_docker_image()
        self.__setup_tap_bridge(simulation, ns3_device)
        self.__start_docker_container(simulation)
        self.__setup_veth(node_ip)
        self.channel_counter += 1
        DockerNode.interface_counter += 1

    def execute_command(self, command):
        """Executes a command as default user.
        """
        self.container.exec_run(command)
