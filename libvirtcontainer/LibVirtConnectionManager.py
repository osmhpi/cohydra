import libvirt


class LibVirtConnectionManager:

    connections = {}

    @staticmethod
    def get_connection_to(target):
        if target == "lxc":
            target = "lxc://"
        if target not in LibVirtConnectionManager.connections:
            LibVirtConnectionManager.connections[target] = libvirt.open(target)
        return LibVirtConnectionManager.connections[target]
