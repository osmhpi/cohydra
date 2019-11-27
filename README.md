# NS-3 Docker Simulation

Network Simulation based on NS3 and Docker, with the help of NS3 docs, Docker docs and some ideas from some research papers.

![NS3 Docker Emulator Schema](NS3DockerEmulatorSchema.png)

This repo provides a python package called `ns3d`.
 
## Installation

> If you are installing this for development, please consider your [development setup options](#development)

*Caution:* This project fiddles with your network interfaces. Please consider to use it in a virtual machine for testing purposes.

Please [install docker](https://docs.docker.com/install/linux/docker-ce/debian/) beforehand and ensure, that the current user is member of the *docker* group.

Install requirements:
```
apt install git make pipenv curl
```

To install the required dependencies and ns-3, run:
```
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

## Examples Of Usage

To start an example where one host is simply pinging another host, type:

```sh
make shell
./example.py
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

## Monitoring

You can use Grafana and InfluxDB to monitor various parameters of the Scenarios. By default, docker containers are monitored with their CPU and memory usage.
To enable monitoring, run `docker-compose up`, which starts the services defined in [docker-compose.yaml](./docker-compose.yaml).