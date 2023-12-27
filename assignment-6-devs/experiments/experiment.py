from pypdevs.simulator import Simulator

from components.sidemarker import SideMarker



model = SideMarker("sidemarker_0")
simulator = Simulator(model)

simulator.setTerminationTime(24*60*60)  # Time-based termination
simulator.setClassicDEVS()      # Instead of parallel
simulator.setVerbose()          # Simulator tracks all events/state changes?

simulator.simulate()
