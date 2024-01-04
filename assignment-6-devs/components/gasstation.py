import uuid
import numpy as np

from dataclasses import dataclass, field, InitVar
from typing import Tuple, List

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import Car, QueryAck, Query
from other.constants import REFUEL_DELAY_MU, REFUEL_DELAY_STD, REFUEL_DELAY_MIN



@dataclass
class GasStationState:
    is_available: bool = True
    """Whether the GasStation is available. The component is available by default."""
    car_queue: List[Tuple[Car, float]] = field(default_factory=list)
    """The priority queue of pairs of Car events to output from the GasStation's car_out port AND their refuel delay time."""
    next_car: Car | None = None
    """The next Car event to output from the GasStation's car_out port."""
    next_car_Ack: QueryAck | None = None
    """The QueryAck that signifies that the next car may be sent to the car_out port."""
    rng_seed: InitVar[int | None] = None
    """The seed for the RNG. Defaults to seed None, which represents a randomized seed that is chosen at runtime. So the default seed does not guarantee that two sequential simulations will sample the same random values using the RNG."""
    rng: np.random.Generator = field(init=False)
    """The RNG used for sampling the Car refueling delay time values from a normal dist."""

    # Timers
    next_car_delay_time: float = INFINITY
    """A delay variable used to decide when the next car should be output."""
    observ_delay_time: float = INFINITY
    """A delay variable used to keep track of how much time passed since the previous Query was sent on Q_send."""

    def __post_init__(self, rng_seed: InitVar[int | None]):
        self.rng = np.random.default_rng(rng_seed)

    def __repr__(self) -> str:
        return f"""GasStation(
                        is_available        = {self.is_available},
                        car_queue           = {[f'ID={car.ID} | no_gas={car.no_gas} | refuel_delay={refuel_delay}' for car, refuel_delay in self.car_queue]},
                        next_car            = {f'ID={self.next_car.ID} | no_gas={self.next_car.no_gas}' if self.next_car is not None else None},
                        next_car_Ack        = {self.next_car_Ack},
                        next_car_delay_time = {self.next_car_delay_time},
                        observ_delay_time   = {self.observ_delay_time},
                        rng_seed            = {self.rng_seed},
"""



class GasStation(AtomicDEVS):
    """Represents the notion that some Cars need gas. It can store an infinite amount of Cars,
    who stay for a certain delay inside an internal queue. This component can be available (default) or unavailable

    This component can be available (default) or unavailable
    """
    def __init__(self, block_name: str, observ_delay: float = 0.1,
                 rng_seed: int | None = None):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        :param observ_delay: The interval at which the GasStation must poll if the received QueryAck has an infinite delay. Defaults to 0.1.
        """
        super(GasStation, self).__init__(block_name)

        self.state: GasStationState = GasStationState(rng_seed=rng_seed)

        # Immutable members -- should NOT be part of the model state member
        self.observ_delay: float = observ_delay
        self.REFUEL_DELAY_MU: float  = REFUEL_DELAY_MU
        self.REFUEL_DELAY_STD: float = REFUEL_DELAY_STD
        self.REFUEL_DELAY_MIN: float = REFUEL_DELAY_MIN

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
        if self._is_queue_empty():
            return INFINITY

        # Yes Cars.
        # If the component is available, THEN the non-refuel delay timers are GUARANTEED to currently be INFINITY.
        # Else, other timers MUST take precedence, so assume refuel delay to be INFINITY.
        shortest_refuel_delay: float = INFINITY
        if self._is_available():
            shortest_refuel_delay = self._get_car_queue_elem_shortest_refuel()[1]   # May or may not be 0.0s

        # Always EXACTLY ONE of the following timers is finite, the rest are infinite.
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
            # Least remaining delay is at the front of queue (ascending order)
            # i.e.
            #       [('a', 0.0s), ('b', 2.0s)]                  | pre-append
            # ==>   [('a', 0.0s), ('b', 2.0s), ('c', 0.0s)]     | post-append
            # ==>   [('a', 0.0s), ('c', 0.0s), ('b', 2.0s)]     | sorted
            # Because new items are appended to the back of the queue.
            self.state.car_queue = sorted(self.state.car_queue, key=lambda e: e[1])

            # Statistics
            new_car.gas_station_times.append((self.name, 0.0))

        # A QueryAck induces one of two possible behaviors
        #   1) do Query polling
        #   2) let new Car leave the gas station after QueryAck.t_until_dep
        if self.Q_rack in inputs:
            query_ack: QueryAck = inputs[self.Q_rack]

            # Ignore ALL QueryAcks that are not meant for this AtomicDEVS component.
            if self.state.next_car is None or self.state.next_car.ID != query_ack.ID:
                return self.state

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
                # Select the Car to output
                self.state.next_car.no_gas = False

        return self.state
    
    def outputFnc(self):
        """May NOT edit state."""
        
        # IF available, the outputFnc is reached when a refuel delay
        # timer in the car queue reaches 0.0s.
        if self._is_available():
            return {
                self.Q_send: Query(self._get_car_queue_elem_shortest_refuel()[0].ID, source=self.name)
            }

        # ELIF polling, the outputFnc is reached when the observ delay
        # timer reaches 0.0s
        if self._should_poll():
            return {
                self.Q_send: Query(self.state.next_car.ID, source=self.name)
            }

        # ELSE car output, the outputFnc is reached when the next car delay
        # timer reaches 0.0s
        return {
            self.car_out: self.state.next_car
        }


    def intTransition(self):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.timeAdvance())

        # After sending the initial/non-polling Query ...
        # OR After sending a subsequent/polling Query ...
        if self._is_available() or self.state.observ_delay_time == 0.0:
            if self._is_available():
                # Prevent further initial/non-polling Queries
                self._set_available(False)
                # Choose the Car that will be output next.
                # Choosing next_car now allows us to ignore any
                # received QueryAck when:
                #   a) next_car is None
                #   b) QueryAck.ID != next_car.ID
                self.state.next_car = self._get_car_queue_elem_shortest_refuel()[0]

            # Be idle until QueryAck received, so set all timers to INFINITY
            self.state.observ_delay_time   = INFINITY
            self.state.next_car_delay_time = INFINITY

        # After outputting a Car ...
        elif self.state.next_car_delay_time == 0.0:
            # Evict the leaving Car from the car queue
            self.state.car_queue.pop(0)
            self.state.next_car = None
            # Reset decision making state variables
            self._set_available(True)
            self.state.next_car_Ack = None
            # Give precedence to refuel timers, so set all non-refueling timers to INFINITY
            self.state.observ_delay_time   = INFINITY
            self.state.next_car_delay_time = INFINITY

        return self.state

    def _is_queue_empty(self) -> bool:
        """Check whether the car queue is empty."""
        return len(self.state.car_queue) == 0

    def _is_available(self) -> bool:
        """Check whether the GasStation component is available."""
        return self.state.is_available
    
    def _set_available(self, available: bool) -> None:
        """Set the availability status of the component."""
        self.state.is_available = available

    def _is_ack_received(self) -> bool:
        """Check whether a QueryAck has been received."""
        return self.state.next_car_Ack is not None

    def _should_poll(self) -> bool:
        """Check whether the current state indicates that polling should happen."""
        if self._is_ack_received():
            return self.state.next_car_Ack.t_until_dep == INFINITY
        return False

    def _get_car_queue_elem_shortest_refuel(self) -> Tuple[Car, float] | None:
        """Get the (Car, refuel delay) tuple with the shortest refuel delay in the car queue.
        
        Multiple pairs may be tied for the same shortest refuel delay.
        * If NO `extTransition()` happens between two subsequent calls of this method,
          then the output tuples for both calls ARE guaranteed to be the same .
        * If an `extTransition()` call DOES happen between two subsequent calls of this
          method, then the two calls are NOT guaranteed to yield the same tuple,
          i.e. the Cars and or timer values of their respective output tuples may differ.

        Returns None if there is no Car in the queue.
        """
        if self._is_queue_empty():
            return None
        return self.state.car_queue[0]

    def _update_multiple_timers(self, time_delta: float) -> None:
        """Update the internal countdown timers of the GasStation component, by decreasing them with *time_delta*.
        
        Implements the bulk of pattern 3: multiple timers.
        """
        # Update multiple Car refuel delay timers
        self.state.car_queue = [
            (car, max(0.0, refuel_delay - time_delta))
            for car, refuel_delay in self.state.car_queue
        ]
        # Update gas station time statistics
        for car, _ in self.state.car_queue:
            # A car added to the car queue was assigned a new tuple
            car.gas_station_times[-1] = (self.name, car.gas_station_times[-1][1] + time_delta)

        # mex(0.0, timer) not needed for following timers, all are INFINITY except for the running/relevant timer
        self.state.observ_delay_time = max(0.0, self.state.observ_delay_time - time_delta)
        self.state.next_car_delay_time = max(0.0, self.state.next_car_delay_time - time_delta)
