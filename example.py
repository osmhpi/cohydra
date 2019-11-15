from ns3d import Network, Node, Scenario

def main():
    scenario = Scenario()

    net = Network("10.0.0.0", "255.255.255.0")

    node1 = Node(docker_build_dir='./docker')
    node2 = Node(docker_build_dir='./docker')
    net.connect(node1, node2)

    scenario.add_network(net)
    with scenario.prepare() as sim:
        sim.simulate(30)

if __name__ == "__main__":
    main()
