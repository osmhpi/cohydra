import ns.core


def prepare_simulation():
    ns.core.GlobalValue.Bind("SimulatorImplementationType", ns.core.StringValue("ns3::RealtimeSimulatorImpl"))
    ns.core.GlobalValue.Bind("ChecksumEnabled", ns.core.BooleanValue("true"))


def start_simulation(runtime=6000):
    ns.core.Simulator.Stop(ns.core.Seconds(runtime))
    print("Start Simulation")
    ns.core.Simulator.Run(signal_check_frequency=-1)
    print("Simulation stopped")


def destroy_simulation():
    ns.core.Simulator.Destroy()
