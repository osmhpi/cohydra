def do_not_filter_bridge_traffic():
    print("Prepare testbed for using bridge devices on linux")

    def overwrite_content_in_file(path, content):
        f = open(path, "w")
        f.write(content)

    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-call-arptables", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-call-iptables", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-filter-vlan-tagged", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-call-ip6tables", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-filter-pppoe-tagged", "0")
    overwrite_content_in_file("/proc/sys/net/bridge/bridge-nf-pass-vlan-input-dev", "0")
