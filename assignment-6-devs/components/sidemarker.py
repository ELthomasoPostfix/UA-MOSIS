from dataclasses import dataclass

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import QueryAck



@dataclass
class SideMarkerState:
    query_ack: QueryAck | None = None
    """The QueryAck passed to a SideMarker is passed along immediately, so a queue is unnecessary."""


class SideMarker(AtomicDEVS):
    """Marks all inputted QueryAcks to have sideways set to true. It also immediately outputs the inputted events.

    This block should be placed in-between the (Q_sack, Q_rack) connection of two RoadSegments if both want to merge onto a third RoadSegment.
    """
    def __init__(self, block_name: str):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        """
        super(SideMarker, self).__init__(block_name)

        self.state = SideMarkerState()

        # Ports
        self.mi = self.addInPort("mi")
        """Port that receives QueryAcks. Immediately marks these events to have sideways set to true. Next, it outputs the QueryAck at once."""
        self.mo = self.addOutPort("mo")
        """Port that outputs the QueryAcks again, at the same time as they were entered."""

    def timeAdvance(self):
        """May NOT edit state."""
        # Immediately output QueryAck IF one is queued/stored
        if self.state.query_ack is not None:
            return 0.0
        # ELSE idle
        return INFINITY

    def extTransition(self, inputs):
        """May edit state."""
        if self.mi in inputs:
            query_ack: QueryAck = inputs[self.mi]
            query_ack.sideways = True
            self.state.query_ack = query_ack    # Store QueryAck to pass along
        return self.state
    
    def outputFnc(self):
        """May NOT edit state."""
        if self.state.query_ack is None:
            return {}
        return {
            self.mo: self.state.query_ack
        }

    def intTransition(self):
        """May edit state."""
        self.state.query_ack = None     # Optional cleanup
        return self.state
