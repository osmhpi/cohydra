import docker

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
            self.docker_image = client.images.build(path=self.docker_build_dir, dockerfile=self.dockerfile)[0].id
        else:
            client.images.pull(self.docker_image)

    def __stop_docker_container(self):
        if self.container is not None:
            self.container.stop()
            self.container = None

    def prepare(self):
        """Prepares the node by building the docker container and ?
        """
        if not self.is_prepared:
            self.__build_docker_image()
            self.is_prepared = True


    def teardown(self):
        self.__stop_docker_container()
