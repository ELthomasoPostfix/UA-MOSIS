from dataclasses import dataclass

from pypdevs.DEVS import AtomicDEVS

from components.messages import Car


@dataclass
class CollectorState:
    simulated_time: float = 0.0
    """Pattern 2: simulated time. It represents a timer that started when the simulation began. Note that this value is only updated in extTransition(), so the simulated time is accurate up until the moment where the last external event was received."""
    n: int = 0
    """The amount of Cars that have exited the simulation/system."""


class Collector(AtomicDEVS):
    """Collects Cars from the simulation and stores all important information such that statistics can be computed afterwards."""
    def __init__(self, block_name: str):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(Collector, self).__init__(block_name)

        self.state: CollectorState = CollectorState()

        # ports
        self.car_in = self.addInPort("car_in")
        """Port that receives the Cars to collect. It can be useful to already compute some statistics upon the arrival of new Cars."""

    def extTransition(self, inputs):
        """May edit state."""
        # Update simulation time
        self.state.simulated_time += self.elapsed
        # Collect Car statistics
        if self.car_in in inputs:
            car: Car = inputs[self.car_in]
            self.state.n += 1 
        return self.state

    # Don't define anything else, as we only store events/statistics.
    # Collector has no behaviour of its own, so the internal transition
    # function does not need to increase the simulated time using the
    # time advance, as pattern 2 normally does.
