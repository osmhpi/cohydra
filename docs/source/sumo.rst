***********************
Using SUMO With testbed
***********************

For simulating the movement of wireless network participants, testbed provides a connection to
the `SUMO <https://sumo.dlr.de/>`_ simulator.

There are two ways to use SUMO with the testbed. In either way, the testbed uses the `TraCI <https://sumo.dlr.de/docs/TraCI.html>`_
Python library to connect to the SUMO instance, running as server.

Install SUMO On Simulation Host
###############################

You can install SUMO directly onto the simulation host. On Debian-based machines, this can be achievd by executing: ::

    sudo apt-get install sumo sumo-tools sumo-docs


After that you can start the simulation and load your configuration files.
You have to provide a port for TraCI: ::

    sumo-gui --remote-port 8813 -c /path/to/configuration

**Important:** testbed relies on the TraCI Python library.
If you use testbed *without Docker*, you need to ensure that testbed can find the library.
Set the :code:`PYTHONPATH` environment variable accordingly: ::

    export PYTHONPATH="/usr/share/sumo/tools:$PYTHONPATH"


Using Docker
############

SUMO can also be used with Docker.
There is a `Github repository <https://github.com/bogaotory/docker-sumo.git>`_ with instructions on how to build the images.
After building the image, the simulation can be started with a new container.
Make sure to properly setup your volume mounts.

::

    $ docker run -it --rm \
        --net host \
        --pid host \
        --userns host \
        --privileged \
        --cap-add=ALL \
        --env="DISPLAY" \
        -v "/etc/group:/etc/group:ro" \
        -v "/etc/passwd:/etc/passwd:ro" \
        -v "/etc/shadow:/etc/shadow:ro" \
        -v "/etc/sudoers.d:/etc/sudoers.d:ro" \
        -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
        --user=$(id -u) \
        -w /workspace \
        -v /path/to/configuration-folder:/workspace \
        mgjm/sumo \
        bash

Now you can proceed like in the local installation:
::

    sumo-gui --remote-port 8813 -c /workspace/path/to/scenario.sumocfg

Writing A Scenario With Testbed
===============================

The simulation can now be configured to use SUMO with the :class:`.SUMOMobilityInput` class.
Please configure the port and host accordingly.
Furthermore, nodes have to be mapped to SUMO IDs in order to be moved by the co-simulation.

.. code-block:: python

    from testbed.mobility_input import SUMOMobilityInput
    #...
    # Scenario creation
    #...
    sumo = SUMOMobilityInput(name='Some title')
    sumo.add_node_to_mapping(car, 'car0', obj_type='vehicle')
    scenario.add_mobility_input(sumo)
    #...
    # Simulation run
    #...
