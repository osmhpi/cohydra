#!/bin/sh

ETH0=$(ip a | grep eth0 | wc -l) # This is for ALPINE

while [ $ETH0 -eq 0 ]
do
  echo "waiting ... "
  sleep 2
  ETH0=$(ip a | grep eth0 | wc -l)
done

ip a > /var/log/ip.txt

tail -f /dev/null

# while true;
# do
#     ping 10.12.0.1
# done
