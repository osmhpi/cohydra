# NS-3 Docker Simulation

Network Simulation based on NS3 and Docker, with the help of NS3 docs, Docker docs and some ideas from some research papers.

![NS3 Docker Emulator Schema](NS3DockerEmulatorSchema.png)

This repo provides a python package called `ns3d`.
 
## Installation

> If you are installing this for development, please consider your [development setup options](#development)

*Caution:* This project fiddles with your network interfaces. Please consider to use it in a virtual machine for testing purposes.

Please [install docker](https://docs.docker.com/install/linux/docker-ce/debian/) beforehand and ensure, that the current user is member of the *docker* group.
You probably also need [docker-compose](http://docs.docker.com/compose/install).

Install requirements:
```sh
apt-get install -y --no-install-recommends pipenv curl bzip2 make git g++ python3-dev llvm llvm-dev clang cmake libclang-dev zlib1g-dev qt5-default
```

To install the required dependencies and ns-3, run:
```sh
make shell
make init
```

After that, please use a python virtual environment for testing: `make shell`.
You always need to be in the environment to run simulations.

## Development
The project contains configuration for VS Code.

To setup the VS Code related stuff run `make vscode-setup`.

### With Docker (Windows and Mac only)
You can open the VS Code Remote Container specified in [`.devcontainer`](.devcontainer).

### With a Debian VM:
You can also use VS Code Remote SSH to connect to your VM or install VS Code inside your VM and develop natively.

### Documentation

For building the documentation, you need to install `doxygen`:

```sh
sudo apt install doxygen
```

After that you can run `make docs` to build the HTML and PDF docs.
The output files are in `docs/html/index.html` and `docs/latex/ns3d-refman.pdf`.

## Examples Of Usage

To start an example where one host is simply pinging another host, type:

```sh
make shell
./examples/basic_example.py
```

Also have a look at the usage of [bridges](./bridge_example.py) or bridges in connection with [a webserver](./webserver_example.py).

## Writing your own simulations

Please note that the `ns3-eth0` interface is added to the docker container, after it startet. Therefore, you need to wait before your container can start using the network. You can copy the [`entrypoint.sh`](docker/ping/entrypoint.sh) to your docker image and add the following lines to your `Dockerfile`:
```dockerfile
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
```

**Important:** The node names of all nodes in the simulation are added to the host files. Therefore you can do something like:

```sh
ping pong
```

The simulation host will be available as **host**, so please do not name a container in this manner.

### Using SUMO (MobilityInput)

In order to use SUMO with the testbed, you need to install it first. You can compile it yourself or install it via `apt`:
```sh
sudo apt-get install sumo sumo-tools sumo-doc
```

After installing, you need to set the `SUMO_HOME` environment variable to the SUMO install directory (containing `bin` and `tools`).
When you chose the way using `apt`, the following path is correct.
```sh
export SUMO_HOME=/usr/share/sumo
```

Then you can start your simulation.

## Monitoring

You can use Grafana and InfluxDB to monitor various parameters of the Scenarios. By default, docker containers are monitored with their CPU and memory usage.
To enable monitoring, run `docker-compose up`, which starts the services defined in [docker-compose.yaml](./docker-compose.yaml).