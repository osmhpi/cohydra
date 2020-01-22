## Disable DHCP
```sh
sudo service dhcpcd stop
sudo update-rc.d -f dhcpcd remove
```

## Static IP
`/etc/network/interfaces`
```
auto eth0
iface eth0 inet static
  address 10.242.42.<ip>/42
  gateway 10.242.42.1
```

## Setup network via gateway
```
ip a a 10.200.1.21/24 dev eth0 noprefixroute
ip r a 10.200.1.0/24 via 10.242.42.1 dev eth0 src 10.200.1.21
```
