#!/bin/sh

until ip a show eth0 &> /dev/null
do
  echo 'waiting for network connection ...'
  sleep 1
done

exec "$@"
