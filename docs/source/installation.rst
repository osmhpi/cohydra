Installation
============

Running cohydra requires some dependencies. We therefore recommend using the Docker images provided below.

Installation With Docker
************************

Cohydra can be obtained via docker.
The easiest solution is using the VSCode *Remote - Containers* extension.
After cloning the repository and opening it in the container, your scenarios will by executing them with :code:`python3`.

Otherwise, you can build the [Dockerfile](./Dockerfile) in the project's root directory yourself by running :code:`make`.
In the container, cohydra will be added to your :code:`PYTHONPATH`.
But you need to make sure, that you run the container with privileges to access the host network in order to have access to the host's network interfaces.
The Docker socket is mounted into the container to enable creating new containers from within the simulation.
You of course need to modify the volume mount to allow cohydra access to your scenarios:

::
    $ docker run -it --rm --cap-add=ALL \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /var/lib/lxd:/var/lib/lxd \
        -v /var/snap/lxd/common/lxd:/var/snap/lxd/common/lxd \
        --net host \
        --pid host \
        --userns host \
        --privileged \
        osmhpi/cohydra:latest

The main image is based on the images in the :src:`docker <docker>` directory.
The :src:`cohydra-base <docker/cohydra-base/Dockerfile>` installs all neccessary dependencies for cohydra,
:src:`cohydra-dev <docker/cohydra-dev/Dockerfile>` is for development purposes (docker-cli in the container).

Local Installation Without Docker
*********************************

In the case you do not want to use the prebuilt docker, a normal ns-3 installation with *NetAnim* Python bindings will work, too.
The Python libraries / directory provided by ns-3 has to be in your :code:`PYTHONPATH`, though.
Cohydra so far has only been tested with **Debian 10 Buster**, **Ubuntu 18.04 Bionic Beaver** and **ns-3.30**.

There is no installation via :code:`pip`.
