from dataclasses import dataclass, field
from typing import List

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import QueryAck



@dataclass
class SideMarkerState:
    query_ack_queue: List[QueryAck] = field(default_factory=list)
    """The queue of QueryAcks passed to a SideMarker, which are passed along immediately. A queue is required because more than one QueryAck may arrive within the same moment."""


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
        if self._is_acks_received():
            return 0.0
        # ELSE idle
        return INFINITY

    def extTransition(self, inputs):
        """May edit state."""
        if self.mi in inputs:
            query_ack: QueryAck = inputs[self.mi]
            query_ack.sideways = True
            self.state.query_ack_queue.append(query_ack)
        return self.state
    
    def outputFnc(self):
        """May NOT edit state."""

        if self._is_acks_received():
            return {
                self.mo: self.state.query_ack_queue[-1]
            }

        return {}

    def intTransition(self):
        """May edit state."""
        if self._is_acks_received():
            self.state.query_ack_queue.pop()
        return self.state

    def _is_acks_received(self) -> bool:
        """Check whether any QueryAcks have been received"""
        return len(self.state.query_ack_queue) > 0
