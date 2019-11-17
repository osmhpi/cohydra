# NS-3 Docker Simulation

Network Simulation based on NS3 and Docker, with the help of NS3 docs, Docker docs and some ideas from some research papers.

![NS3 Docker Emulator Schema](http://d2r9k1wfjzxupg.cloudfront.net/NS3DockerEmulatorSchema-min.png)

This repo provides a python package called `ns3d`.
 
# Installation

*Caution:* This project fiddles with your network interfaces. Please consider to use it in a virtual machine for testing purposes.

Please install docker beforehand and ensure, that the current user is member of the *docker* group.

To install the required dependencies and ns-3, run:
```
make shell
make init
```

After that, please use a python virtual environment for testing: `make shell`.
You always need to be in the environment to run simulations.

# Examples Of Usage

The simulations need to be run as `root` user, because network devices are created during simulation.
To start an example where one host is simply pinging another host, type:

```
sudo make shell
./example.py
```