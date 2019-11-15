import docker
import logging

class Node:
    """A node is representing a docker container.
    """

    def __init__(self, docker_image=None, docker_build_dir=None, dockerfile='Dockerfile'):
        self.docker_image = docker_image
        self.docker_build_dir = docker_build_dir
        self.dockerfile = dockerfile
        self.is_prepared = False
        self.container = None
        self.interfaces = list()
        if docker_build_dir is None and docker_image is None:
            raise Exception('Please specify Docker image or build directory')

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
                                               network_mode='none', detach=True)

    def __stop_docker_container(self):
        logging.info('Stopping docker container: %s', self.container.name)
        if self.container is not None:
            self.container.stop(timeout=1)
            self.container = None

    def prepare(self):
        """Prepares the node by building the docker container and ?
        """
        if not self.is_prepared:
            logging.info('Preparing node')
            self.__build_docker_image()
            self.__start_docker_container()
            self.is_prepared = True
        else:
            logging.info('Node already prepared')


    def teardown(self):
        self.__stop_docker_container()
