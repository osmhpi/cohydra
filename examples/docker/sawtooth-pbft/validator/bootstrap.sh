#!/bin/sh

set -e

until curl -q "http://influxdb:8086/ping" 2> /dev/null; do
    sleep 1
done

for i in  1 2 3 4;
do
    until ping -c1 "validator$i" >/dev/null 2>&1; 
    do
        echo "waiting for validator$i"
    done
done

if [ ! -f /etc/sawtooth/keys/validator.priv ]; then 
    sawadm keygen &&
    cp /etc/sawtooth/keys/validator.pub /etc/sawtooth/pubkeys/$HOSTNAME.pub
    sawtooth keygen $(whoami) &&
    if [ $HOSTNAME = validator1 ]; then
        sleep 5
        sawset genesis -k $HOME/.sawtooth/keys/$(whoami).priv -o config-genesis.batch
        all_keys=$(/get_public_keys.sh)
        echo $all_keys
        sawset proposal create --key $HOME/.sawtooth/keys/$(whoami).priv\
            -o config-consensus.batch\
            sawtooth.consensus.algorithm.name=pbft\
            sawtooth.consensus.algorithm.version=1.0\
            sawtooth.consensus.pbft.members=$all_keys\
            sawtooth.consensus.pbft.block_publishing_delay=100\
            sawtooth.consensus.pbft.forced_view_change_interval=10
        sawadm genesis config-genesis.batch config-consensus.batch
    fi
fi

settings-tp -C tcp://localhost:4004&
sawtooth-rest-api -v -B 0.0.0.0:8008&
pbft-engine -v&
intkey-tp-python -v&
exec "$@"
