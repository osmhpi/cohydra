import logging
import os
import threading

from nsenter import Namespace
import docker

from ..context import defer
from ..command_executor import DockerCommandExecutor
from .base import Node

logger = logging.getLogger(__name__)

def expand_volume_shorthand(key_value):
    name, spec = key_value
    if isinstance(spec, str):
        return (name, {'bind': spec, 'mode': 'rw'})
    return (name, spec)

def log_to_file(container, log_path, stdout=False, stderr=False):
    log = logging.getLogger(container.name)
    log.debug('Write log to %s', log_path)
    with open(log_path, 'wb', 0) as log_file:
        for line in container.logs(stdout=stdout, stderr=stderr, follow=True, stream=True):
            log.log(logging.INFO if stdout else logging.ERROR, '%s', line.decode().strip())
            log_file.write(line)
        log.debug('Done logging')

class DockerNode(Node):
    """A node is representing a docker container.
    """

    interface_counter = 0

    def __init__(self, name, docker_image=None, docker_build_dir=None, dockerfile='Dockerfile',
                 cpus=0.0, memory=None, command=None, volumes=None, exposed_ports=None):
        super().__init__(name)
        self.docker_image = docker_image
        self.docker_build_dir = docker_build_dir
        self.dockerfile = dockerfile

        self.cpus = cpus
        self.memory = memory

        self.command = command
        self.volumes = dict(map(expand_volume_shorthand, volumes.items())) if volumes else None
        self.exposed_ports = exposed_ports if exposed_ports is not None else dict()

        self.container = None
        self.container_pid = None

        if docker_build_dir is None and docker_image is None:
            raise Exception('Please specify Docker image or build directory')

    @property
    def docker_image_tag(self):
        return f'ns3-{self.name}'

    def wants_ip_stack(self):
        return True

    def prepare(self, simulation):
        """Prepares the node by building the docker container and ?
        """
        logger.info('Preparing node %s', self.name)
        self.build_docker_image()
        self.start_docker_container(simulation.log_directory, simulation.hosts)
        self.setup_interfaces()

    def build_docker_image(self):
        client = docker.from_env()
        if self.docker_image is None:
            logger.info('Building docker image: %s/%s', self.docker_build_dir, self.dockerfile)
            self.docker_image = client.images.build(
                path=self.docker_build_dir,
                dockerfile=self.dockerfile,
                rm=True,
                nocache=False,
            )[0]
        elif isinstance(self.docker_image, str):
            logger.info('Pulling docker image: %s', self.docker_image)
            self.docker_image = client.images.pull(self.docker_image)
        self.docker_image.tag(self.docker_image_tag)

    def start_docker_container(self, log_directory, extra_hosts=None):
        logger.info('Starting docker container: %s', self.name)
        client = docker.from_env()
        self.container = client.containers.run(
            self.docker_image_tag,
            name=self.name,
            hostname=self.name,
            labels={"created-by": "ns-3"},

            remove=True,
            auto_remove=True,
            detach=True,

            privileged=True,
            nano_cpus=int(self.cpus * 1e9),
            mem_limit=0 if self.memory is None else self.memory,

            command=self.command,
            extra_hosts=extra_hosts,
            volumes=self.volumes,
            ports=self.exposed_ports,
        )
        defer(f'stop docker container {self.name}', self.stop_docker_container)

        for stream in ('stdout', 'stderr'):
            log_file_path = os.path.join(log_directory, f'{self.name}.{stream}.log')
            threading.Thread(target=log_to_file, args=(self.container, log_file_path), kwargs={stream: True}).start()

        low_level_client = docker.APIClient()
        self.container_pid = low_level_client.inspect_container(self.container.id)['State']['Pid']

        self.command_executor = DockerCommandExecutor(self.name, self.container)

    def stop_docker_container(self):
        if self.container is not None:
            logger.info('Stopping docker container: %s', self.container.name)
            self.container.stop(timeout=1)
            self.container = None
            self.container_pid = None
            self.command_executor = None

    def setup_interfaces(self):
        for name, interface in self.interfaces.items():
            interface.setup_bridge()
            interface.connect_ns3_device()

            interface.setup_veth_pair({
                'ifname': name,
                "net_ns_fd": f"/proc/{self.container_pid}/ns/net",
            })

            # Get container's namespace and setup the interface in the container
            with Namespace(self.container_pid, 'net'):
                interface.setup_veth_other_end(name)
