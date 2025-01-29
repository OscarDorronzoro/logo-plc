#! /bin/bash

sudo ip address flush dev enp9s0
sudo ip route flush dev enp9s0
sudo ip address add 192.168.0.7/24 brd + dev enp9s0
sudo ip route add 192.168.0.1 dev enp9s0
sudo ip route add default via 192.168.0.1 dev enp9s0
ip a s dev enp9s0

