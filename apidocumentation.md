# API-Dokumentation

## Knoten

### LXD-Container
In `nodes/LXDNode.py`

Unterstützte Funktionen:
```
init(name, image, additional_configs=None) -> LXCContainer-Object
get_ns3_node() -> ns3-Node (ns.network.Node)
create() -> None
_configure_container(config) [private] -> None
start_interfaces() -> None
connect_to_netdevice(network_name, netdevice, ipv4_addr, ip_prefix, bridge_connect=False, bridge_connect_ip=None, bridge_connect_mask=None) -> None
execute_command(command, sudo=False) -> None
start() -> None
stop() -> None
destroy() -> None
```

Nicht unterstützte aber angelegte Funktionen:
```
Keine
```

Subklassen: `NetworkInterface`

### Externe Netzwerke
In `nodes/InterfaceNode.py`

Unterstützte Funktionen:
```
init(name, interface) -> External-Network-Object
get_ns3_node() -> ns3-Node (ns.network.Node)
connect_to_netdevice(network_name, netdevice, ipv4_addr, ip_prefix, bridge_connect=False, bridge_connect_ip=None, bridge_connect_mask=None) -> None
execute_command(ip, user, password, command, sudo=False) -> None
destroy() -> None
```

Nicht unterstützte aber angelegte Funktionen:
```
create()
start()
stop()
```

Subklassen: `NetworkInterface`

## Netzwerke

### CSMA-Netzwerk
In `netsimbridge/CSMANetwork.py`

Unterstützte Funktionen:
```
init(name) -> CSMA-Netzwerk
add_node(system_node, ipv4_addr="255.255.255.255", ipv4_subnetmask="255.255.255.255", bridge_connect=False, bridge_connect_ip="255.255.255.255", bridge_connect_mask="255.255.255.255", connect_on_create=False) -> None
create() -> None
connect_node(node) -> None
connect() -> None
disconnect_node(node) -> None
disconnect -> None
set_delay(delay) -> None
set_data_rate(data_rate) -> None
destroy() -> None
```

Anmerkungen:
- `set_data_rate` hat nur vor `create` einen Effekt.


Nicht unterstützte aber angelegte Funktionen:
```
Keine
```

Subklassen: `ConnectedNode`

### Wifi-Netzwerk (802.11p)
In `netsimbridge/WifiNetwork.py`

Unterstützte Funktionen:
```
init(name) -> Wifi-Netzwerk-Objekt
add_node(system_node, pos_x, pos_y, pos_z, ipv4_addr="255.255.255.255", ipv4_subnetmask="255.255.255.255", bridge_connect=False, bridge_connect_ip="255.255.255.255", bridge_connect_mask="255.255.255.255", connect_on_create=False) -> None
create() -> None
set_delay(delay) -> None
set_data_rate(data_rate) -> None
set_position(system_node, pos_x, pos_y, pos_z) -> None
```

Anmerkungen:
- `set_delay` legt die Latenz bei 100m Distanz fest. Bei 50m ist es dann nur noch die Hälfte.
- `set_data_rate` hat nur vor `create` einen Effekt.
- `set_position` soll langfristig Teil eines Knotens werden.
- `connect_node` enthält noch Code, der jedoch nicht funktionieren sollte.

Nicht unterstützte aber angelegte Funktionen:
```
connect_node(node)
connect()
disconnect_node(node)
disconnect()
destroy()
```

Subklassen: `ConnectedNode`

## Hilfen

### Subnetzmasken-Hilfe
In `helper/SubnetMaskHelper.py`

Unterstützte Funktionen:
```
subnetmask_to_cidr(subnetmask) -> Subnetzmaske in CIDR Notation
```

Nicht unterstützte aber angelegte Funktionen:
```
Keine
```

## Domain-Spezifische Simulation

### SUMO-Simulation
In `simulations/SumoSimulation.py`

Unterstützte Funktionen:
```
init(binary_path, config_path) -> Sumo-Simulations-Objekt
start(after_simulation_step, steps=1000) -> None
add_node_to_mapping(node, sumo_vehicle_id, obj_type="vehicle") -> None
get_position_of_node(node) -> Position des Nodes (2 Integer Werte)
get_distance_between_nodes(node1, node2) -> Euklidischer Abstand zwischen den beiden Knoten (float)
destroy() -> None
```

Anmerkungen:
- `add_node_to_mapping` bis jetzt unterstützte Objekt-Typen: `vehicle`, `person`, `junction`. Mehr sollen noch kommen.

Nicht unterstützte aber angelegte Funktionen:
```
Keine
```

## System-Komponenten

### TUN-Schnittstellen
In `hostcomponents/TunTapDevice.py`

Unterstützte Funktionen:
```
init(name) -> Tun-Tap-Schnittstellen-Objekt
create() -> None
up() -> None
down() -> None
destroy() -> None
```

Nicht unterstützte aber angelegte Funktionen:
```
Keine
```

### Netzwerkbrücken
In `hostcomponents/BridgeDevice.py`

Unterstützte Funktionen:
```
init(name) -> Bridge-Objekt
create() -> None
add_interface(interface) -> None
add_interface_name(interface_name) -> None
del_interface(interface) -> None
up() -> None
connect_veth(veth_ip, veth_mask) -> None
down() -> None
destroy() -> None
```

Anmerkungen:
- `connect_veth` erstellt ein Schnittstellenpaar, welches zusätzlich mit der Bridge verbunden wird, um die anderen verbundenen Schnittstellen erreichbar zu machen.

Nicht unterstützte aber angelegte Funktionen:
```
Keine
```

## Event-Steuerung
In `events/Event.py`

Unterstützte Funktionen:
```
event() [static] -> Neues Event
e() [static] -> Neues Event
init() -> Neues Event
after(seconds) -> self
when(condition, result, globals, locals) -> self
check_if(command, return_code, every=-1) -> self
execute(expression) -> self
start() -> None
s() -> None
start_on_simulation_start() -> None
```

Anmerkungen:
- `s` bezieht sich auf `start`
- `when` soll langfristig auch als Polling-Funktion existieren.

Nicht unterstützte aber angelegte Funktionen:
```
Keine
```

Zusätzliche statische Funktionen: `event_worker`

Subklassen: `EventPart`
