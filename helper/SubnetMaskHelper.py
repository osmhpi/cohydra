def subnetmask_to_cidr(subnetmask):
    cidr = sum(bin(int(part)).count('1') for part in subnetmask.split("."))
    return cidr
