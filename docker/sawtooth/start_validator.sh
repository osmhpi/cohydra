#!/bin/sh

ETH0=$(ip a | grep eth0 | wc -l)

while [ $ETH0 -eq 0 ]
do
  echo "waiting ... "
  sleep 2
  ETH0=$(ip a | grep eth0 | wc -l)
done

bash -c "sawadm keygen && \
    sawtooth keygen my_key && \
    sawset genesis -k /root/.sawtooth/keys/my_key.priv && \
    sawadm genesis config-genesis.batch && \
    sawtooth-validator -vv \
        --endpoint tcp://10.0.0.1:8800 \
        --bind component:tcp://eth0:4004 \
        --bind network:tcp://eth0:8800"