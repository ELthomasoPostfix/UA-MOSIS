import uuid
import numpy as np

from dataclasses import dataclass, field, InitVar
from typing import Tuple, List

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import Car, QueryAck, Query



@dataclass
class GasStationState:
    # TODO imporove is_available docstring
    is_available: bool = True
    """Whether the GasStation is available. The component is available by default."""
    car_queue: List[Tuple[Car, float]] = field(default_factory=list)
    """The priority queue of pairs of Car events to output from the GasStation's car_out port AND their refuel delay time."""
    next_car_Ack: QueryAck | None = None
    """The QueryAck that signifies that the next car may be sent to the car_out port."""
    # TODO next_car_delay_time necessary???
    next_car_delay_time: float = INFINITY
    """A delay variable used to decide when the next car should be output."""
    # TODO observ_delay_time necessary???
    observ_delay_time: float = INFINITY
    """A delay variable used to keep track of how much time passed since the previous Query was sent on Q_send."""
    rng_seed: InitVar[int | None] = None
    """The seed for the RNG. Defaults to seed None, which represents a randomized seed that is chosen at runtime. So the default seed does not guarantee that two sequential simulations will sample the same random values using the RNG."""
    rng: np.random.Generator = field(init=False)
    """The RNG used for sampling the Car refueling delay time values from a normal dist."""

    def __post_init__(self, rng_seed: InitVar[int | None]):
        self.rng = np.random.default_rng(rng_seed)


class GasStation(AtomicDEVS):
    """Represents the notion that some Cars need gas. It can store an infinite amount of Cars,
    who stay for a certain delay inside an internal queue. This component can be available (default) or unavailable

    This component can be available (default) or unavailable
    """
    def __init__(self, block_name: str, observ_delay: float = 0.1):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        :param observ_delay: The interval at which the GasStation must poll if the received QueryAck has an infinite delay. Defaults to 0.1.
        """
        super(GasStation, self).__init__(block_name)

        self.state: GasStationState = GasStationState()

        # Immutable members -- should NOT be part of the model state member
        self.observ_delay: float = observ_delay
        self.REFUEL_DELAY_MU: float  = 10 * 60   # The Car refuel delay time normal dist. mean: 10min = 10 * 60s = 60s
        self.REFUEL_DELAY_STD: float = 130       # The Car refuel delay time normal dist. standard deviation: 130s
        self.REFUEL_DELAY_MIN: float = 120       # The Car refuel delay time minimum value (clamp): 2min = 120s

        # Ports
        self.car_in = self.addInPort("car_in")
        """Cars can enter the GasStation via this port. As soon as one is entered, it is given a delay time, sampled from a normal distribution with mean 10 minutes and standard deviation of 130 seconds. Cars are required to stay at least 2 minutes in the GasStation. When this delay has passed and when this component is available, a Query is sent over the Q_send port."""
        self.Q_rack = self.addInPort("Q_rack")
        """When a QueryAck is received, the GasStation waits for QueryAck's t_until_dep time before outputting the next Car over the car_out output. Only then, this component becomes available again. If the waiting time is infinite, the GasStation keeps polling until it becomes finite again."""
        self.Q_send = self.addOutPort("Q_send")
        """Sends a Query as soon as a Car has waited its delay. Next, this component becomes unavailable, preventing collisions on the RoadSegment after."""
        self.car_out = self.addOutPort("car_out")
        """Outputs the Cars, with no_gas set back to false."""

    def timeAdvance(self):
        """May NOT edit state."""
        # No Cars, be idle
        if self._queue_is_empty():
            return INFINITY

        # Yes Cars.
        # If the component is available, THEN the non-refuel delay timers MUST currently be INFINITY.
        # Else, other timers MUST take precedence, so assume INFINITY refuel delay.
        shortest_refuel_delay: float = INFINITY
        if self._is_available():
            shortest_refuel_delay = self._get_shortest_refuel_delay_elem()[1]   # May or may not be 0.0s

        return min(shortest_refuel_delay,
                   self.state.observ_delay_time,
                   self.state.next_car_delay_time)

    def extTransition(self, inputs):
        """May edit state."""
        # Pattern 3: multiple timers
        # Offset the external interruption of internal timers
        self._update_multiple_timers(self.elapsed)

        # A new Car arrives.
        # The shortest remaining refuel delay of all Cars represents a possible next timeAdvance value.
        if self.car_in in inputs:
            # Generate queue entry
            new_car: Car = inputs[self.car_in]
            refuel_delay_time: float = self.state.rng.normal(self.REFUEL_DELAY_MU, self.REFUEL_DELAY_STD)
            refuel_delay_time = max(self.REFUEL_DELAY_MIN, refuel_delay_time)
            self.state.car_queue.append((new_car, refuel_delay_time))
            # Least remaining delay is at back of queue (ascending order)
            self.state.car_queue = sorted(self.state.car_queue, key=lambda e: e[1], reverse=True)

        # A QueryAck can induce one of two behaviors
        #   1) do Query polling
        #   2) let new Car leave the gas station after QueryAck.t_until_dep
        if self.Q_rack in inputs:
            query_ack: QueryAck = inputs[self.Q_rack]
            self.state.next_car_Ack = query_ack

            # Pattern 3: multiple timers --> set 'irrelevant' timers to INFINITY so that the sole 'relevant' has precedence.
            # Start polling timer.
            if self._should_poll():
                self.state.observ_delay_time = self.observ_delay
                self.state.next_car_delay_time = INFINITY
            # Start Car departure timer.
            else:
                self.state.observ_delay_time = INFINITY
                self.state.next_car_delay_time = self.state.next_car_Ack.t_until_dep

        return self.state
    
    def outputFnc(self):
        """May NOT edit state."""
        
        # IF available, the outputFnc is reached when a refuel delay
        # timer in the car queue reaches 0.0s.
        #
        # ELIF polling, the outputFnc is reached when the observ delay
        # timer reaches 0.0s
        if self._is_available() or self._should_poll():
            return {
                self.Q_send: Query(self._get_shortest_refuel_delay_elem()[0].ID)
            }

        # ELSE car output, the outputFnc is reached when the next car delay
        # timer reaches 0.0s
        leaving_car: Car = self.state.car_queue[self._get_leaving_car_idx()][0]
        return {
            self.car_out: leaving_car
        }


    def intTransition(self):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.timeAdvance())

        # After sending the initial/non-polling Query ...
        # OR After sending a subsequent/polling Query ...
        if self._is_available() or self.state.observ_delay_time == 0.0:
            # Prevent further initial/non-polling Queries
            self._set_available(False)
            # Be idle until QueryAck received, so set all timers to INFINITY
            self.state.observ_delay_time   = INFINITY
            self.state.next_car_delay_time = INFINITY

        # After outputting a Car ...
        elif self.state.next_car_delay_time == 0.0:
            # Evict the leaving Car from the car queue
            output_car_idx: int = self._get_leaving_car_idx()
            self.state.car_queue.pop(output_car_idx)
            # Reset decision making state variables
            self.state.is_available = True
            self.state.next_car_Ack = None
            # Give precedence to refuel timers, so set all non-refueling timers to INFINITY
            self.state.observ_delay_time   = INFINITY
            self.state.next_car_delay_time = INFINITY

        return self.state

    def _queue_is_empty(self) -> bool:
        """Check whether the car queue is empty."""
        return len(self.state.car_queue) == 0

    def _is_available(self) -> bool:
        """Check whether the GasStation component is available."""
        return self.state.is_available
    
    def _set_available(self, available: bool) -> None:
        """Set the availability status of the component."""
        self.state.is_available = available

    def _ack_is_received(self) -> bool:
        """Check whether a QueryAck has been received."""
        return self.state.next_car_Ack is not None

    def _should_poll(self) -> bool:
        """Check whether the current state indicates that polling should happen."""
        if self._ack_is_received():
            return self.state.next_car_Ack.t_until_dep == INFINITY
        return False

    def _get_leaving_car_idx(self) -> int:
        """Get the index in the car queue of the Car matching the received QueryAck.
        
        If that Car is not in the car queue, then the return value defaults to the end/tail
        of the car queue instead, namely index -1.
        
        :return: The index of a leaving Car in the car queue
        """
        assert self._ack_is_received(), "Cannot get idx of leaving Car when no QueryAck has been received."

        ack_car_ID: uuid.UUID = self.state.next_car_Ack.ID
        output_car_idx: int = next(
            (
                idx
                for idx, pair in enumerate(self.state.car_queue)
                if pair[0].ID == ack_car_ID
            ),
            -1
        )
        
        return output_car_idx

    def _get_shortest_refuel_delay_elem(self) -> Tuple[Car, float] | None:
        """Get a pair of (Car, refuel delay) with the shortest refuel delay in the queue.
        
        Multiple pairs may be tied for the same shortest refuel delay.
        Subsequent calls are not guaranteed to yield the same pair, i.e. the Cars may differ.
        """
        if self._queue_is_empty():
            return None
        return self.state.car_queue[-1]

    def _update_multiple_timers(self, time_delta: float) -> None:
        """Update the internal countdown timers of the GasStation component, by decreasing them with *time_delta*.
        
        Implements the bulk of pattern 3: multiple timers.
        """
        # Update multiple Car refuel delay timers
        self.state.car_queue = [
            (car, max(0.0, refuel_delay - time_delta))
            for car, refuel_delay in self.state.car_queue
        ]
        # mex(0.0, timer) not needed for following timers, all are INFINITY except for the running/relevant timer
        self.state.observ_delay_time -= time_delta
        self.state.next_car_delay_time -= time_delta
