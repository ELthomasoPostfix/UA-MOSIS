from dataclasses import dataclass, field
from typing import List, Tuple

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import Car, QueryAck, Query



@dataclass
class RoadSegmentState:
    remaining_x: float
    """The remaining distance that the current Car (i.e., the first one in cars_present) should still travel on this RoadSegment."""
    cars_present: List[Car] = field(default_factory=list)
    """A list for all the Cars on this RoadSegment. Even though the existence of multiple Cars results in a collision, for extensibility purposes a list should be used."""
    t_until_dep: float = 0.0
    """The time until the current Car (i.e., the first one in cars_present) leaves the RoadSegment. If the Car's velocity is 0, this value is infinity. If no Car is present, this value is 0."""
    incoming_queries_queue: List[Tuple[Query, float]] = field(default_factory=list)
    """The FIFO queue of incoming/external Query events. Each queue element is a tuple containing (Query, remaining observe delay time). Because index 0 is the head of the queue, the remaining observe delay time will naturally be ordered in ascending order."""
    # Statistics
    n_enter: int = 0
    """The number of cars that have entered this RoadSegment. See the car_in port description."""
    n_crash: int = 0
    """The number of crashes that have occurred in this RoadSegment. See the car_in port description."""

class RoadSegment(AtomicDEVS):
    """Represents a small stretch of road that can only contain a single Car.
    
    When multiple Cars are on a RoadSegment, we assume the Cars crashed into each other.
    """
    def __init__(self, block_name: str, L: float, v_max: float,
                 observ_delay: float = 0.1, priority: bool = False, lane: int = 0):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        :param L: The length of the RoadSegment. Given that the average Car is about 5 meters in length, a good estimate value for L would therefore be 5 meters.
        :param v_max: The maximal allowed velocity on this RoadSegment.
        :param observ_delay: The time it takes to reply to a Query that was inputted. This value mimics the reaction time of the driver. We can increase the observ_delay to accomodate for bad weather situations (e.g., a lot of fog and/or rain). Defaults to 0.1.
        :param priority: Whether or not this RoadSegment should have priority on a merge with other road segments. Defaults to False.
        :param lane: Indicator of the lane this Roadsegment is currently part of. Defaults to 0.
        """
        super(RoadSegment, self).__init__(block_name)

        self.state: RoadSegmentState = RoadSegmentState(remaining_x=L)

        # Immutable members -- should NOT be part of the model state member
        self.L: float = L
        self.v_max: float = v_max
        self.observ_delay: float = observ_delay
        self.priority: bool = priority
        self.lane: int = lane

        # Ports
        self.car_in = self.addInPort("car_in")
        """All Cars are inputted on this port. As soon as a Car arrives, a Query is outputted over the Q_send port. For statistical purposes, the number of Cars that enter this RoadSegment should be maintained.\n\n If there already was a Car on the RoadSegment, a collision occurs. We will make the incredibly bold assumption that a crash results in total vaporization of both Cars, removing them from the simulation. For statistical purposes, the number of crashes in each RoadSegment should be maintained."""
        self.Q_recv = self.addInPort("Q_recv")
        """Port that receives Query events. Upon arrival of a Query, the RoadSegment waits for observ_delay time before replying a QueryAck on the Q_sack output port. The outputted QueryAck's t_until_dep equals the remaining time of the current Car on the RoadSegment (which can be infinity if the Car's velocity is 0). If there is no Car, t_until_dep equals zero.\n\n Notice that multiple Query events may arrive during this waiting time, all of whom should wait for exactly observ_delay time."""
        self.Q_rack = self.addInPort("Q_rack")
        """Port that receives QueryAck events. When such an event is received, the Car updates its velocity v to v_new as described in the asssignment."""

        self.car_out = self.addOutPort("car_out")
        """Outputs the Car on this RoadSegment if it has traveled it completely. The Car's distance_traveled should be increased by L."""
        self.Q_send  = self.addOutPort("Q_send")
        """Sends a Query as soon as a new Car arrives on this RoadSegment (if there was no crash). Additionally, a Query is sent every observ_delay time if the Car's v equals 0."""
        self.Q_sack  = self.addOutPort("Q_sack")
        """Replies a QueryAck to a Query. The QueryAck's t_until_dep equals the remaining time of the current Car on the RoadSegment (which can be infinity if the Car's velocity is 0). If there is no Car, t_until_dep equals zero. The QueryAck's lane is set w.r.t. the RoadSegment's lane; and the QueryAck's sideways is set to be false here."""

    def timeAdvance(self):
        """May NOT edit state."""

        # The Query observ delay timer nearest to expiration.
        # Is a value in the range: [ 0.0, self.observ_delay ] U INFINITY
        shortest_observ_delay: float = self._get_shortest_observ_delay()

        return min(shortest_observ_delay)

    def extTransition(self, inputs):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.elapsed)

        # Enqueue an incoming Query event on the FIFO queue
        if self.Q_recv in inputs:
            query: Query = inputs[self.Q_recv]
            self.state.incoming_queries_queue.append((query, self.observ_delay))

        return self.state
    
    def outputFnc(self):
        """May NOT edit state."""

        if self._should_sack():
            query: Query = self.state.incoming_queries_queue[0][0]
            # TODO is this t_until_dep given to the QueryAck correctly calculated at this moment????
            return {
                self.Q_sack: QueryAck(query.ID, self.state.t_until_dep, self.lane, sideways=False)
            }

        return {
        }

    def intTransition(self):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.timeAdvance())

        # After sending a QueryAck in reply to a Query ...
        if self._should_sack():
            self.state.incoming_queries_queue.pop(0)

        return self.state

    def car_enter(self, car: Car) -> None:
        """Handles all the logic of a *car* entering the RoadSegment.
        
        Can be called to pre-fill the RoadSegment with a Car.
        """
        if len(self.state.cars_present) >= 1:
            # TODO Collision occurred
            return
        
        self.state.cars_present.append(car)

    def _is_query_received(self) -> bool:
        """Check whether any incoming Query is currently being processed."""
        return len(self.state.incoming_queries_queue) > 0
    
    def _get_shortest_observ_delay(self) -> float:
        """Get the shortest remaining observe delay associated with any incoming Query.
        
        If there are no incoming Queries, then the output defaults to INFINITY.
        """
        if self._is_query_received():
            return self.state.incoming_queries_queue[0][1]
        return INFINITY

    def _should_sack(self) -> bool:
        """Check whether a QueryAck should be sent in response to the expiration of an observ delay timer for an incoming Query, according to the current state."""
        return self._get_shortest_observ_delay() == 0.0

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp the *value* to the fully closed interval `[ min_val, max_val ]`."""
        return min(max(value, min_val), max_val)

    def _update_multiple_timers(self, time_delta: float) -> None:
        """Update the internal countdown timers of the RoadSegment component, by decreasing them with *time_delta*.
        
        Implements the bulk of pattern 3: multiple timers.
        """
        # Update incoming Query observe delay timers
        # mex(0.0, timer) not needed for following timers, each Query is responded to as soon as their timer reaches 0.0s.
        self.state.incoming_queries_queue = [
            (query, observ_delay_remaining - time_delta)
            for query, observ_delay_remaining in self.state.incoming_queries_queue
        ]
        # mex(0.0, timer) not needed for following timers, all are INFINITY except for the running/relevant timer
        # TODO fill this section out???
