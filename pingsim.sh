#!/usr/bin/env bash

COUNTER=0
MAIN_SCRIPT="main.new.py"

NODES=10 # Number of nodes
TIMEEMU=10 # Time of the emulation in seconds
SIZE=300 # Size of the network, 300m x 300m
SPEED=5 # Speed in m/s
PAUSE=0 # Pause time of the nodes in seconds
NUM_EMULATIONS=2

export BAKE_HOME=/home/test/Documents/ns3docker/workspace/bake
export NS3_HOME=$BAKE_HOME/../source/ns-3.29

# We create everything
python3 ${MAIN_SCRIPT} -n ${NODES} -t ${TIMEEMU} -s ${SIZE} -ns ${SPEED} -np ${PAUSE} create
# We run the NS3 simulation
python3 ${MAIN_SCRIPT} -n ${NODES} -t ${TIMEEMU} -s ${SIZE} -ns ${SPEED} -np ${PAUSE} ns3

while [  $COUNTER -lt $NUM_EMULATIONS ]; do

    DATENOW=$(date +"%y_%m_%d_%H_%M")

    # Making a backup from the last iteration's logs
    echo "---------------------------"
    echo ${DATENOW}
    echo "---------------------------"
    sudo mkdir -p var/archive/${DATENOW}
    sudo mv var/log/* var/archive/${DATENOW}/

    # Run the emulation
    python3 ${MAIN_SCRIPT} -n ${NODES} -t ${TIMEEMU} -s ${SIZE} -ns ${SPEED} -np ${PAUSE} emulation

    ####################################################################
    # Run a custom script to gather data from the logs for further analysis
    # python3 statscollector2.py bla bla bla
    ####################################################################

	let COUNTER=COUNTER+1
done

# We destroy everything cause we don't need it anymore
python3 ${MAIN_SCRIPT} -n ${NODES} -t ${TIMEEMU} -s ${SIZE} -ns ${SPEED} -np ${PAUSE} destroy
