#!/bin/sh

sawadm keygen
sawtooth keygen my_key
sawset genesis -k /root/.sawtooth/keys/my_key.priv
sawadm genesis config-genesis.batch
sawtooth-validator -vv \
  --endpoint tcp://validator:8800 \
  --bind component:tcp://ns3-eth0:4004 \
  --bind network:tcp://ns3-eth0:8800