#!/bin/sh

ETH0=$(ip a | grep eth0 | wc -l)

while [ $ETH0 -eq 0 ]
do
  echo "waiting ... "
  sleep 2
  ETH0=$(ip a | grep eth0 | wc -l)
done

bash -c "sawtooth keygen && tail -f /dev/null"