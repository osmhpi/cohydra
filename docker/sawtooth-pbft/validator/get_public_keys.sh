#!/bin/bash

function join { local IFS="$1"; shift; echo -ne "$*"; }

pubkeys=()

for file in /etc/sawtooth/pubkeys/*
do
    pubkeys+=(\"$(cat $file)\")
done

result=$(join , ${pubkeys[@]})
echo -ne [$result]