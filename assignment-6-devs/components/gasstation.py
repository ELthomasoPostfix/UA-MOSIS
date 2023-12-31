import uuid
import numpy as np

from dataclasses import dataclass, field, InitVar
from typing import Tuple, List

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import Car, QueryAck, Query

from other.query_polling_state import QueryPollingState



@dataclass
class GasStationState(QueryPollingState):
    is_available: bool = True
    """Whether the GasStation is available. The component is available by default."""
    car_queue: List[Tuple[Car, float]] = field(default_factory=list)
    """The priority queue of pairs of Car events to output from the GasStation's car_out port AND their refuel delay time."""
    awaiting_initial_ack: bool = False
    """Whether or not we are awaiting the initial QueryAck."""
    next_car_delay_time: float = INFINITY
    """A delay variable used to decide when the next car should be output."""
    rng_seed: InitVar[int | None] = None
    """The seed for the RNG. Defaults to seed None, which represents a randomized seed that is chosen at runtime. So the default seed does not guarantee that two sequential simulations will sample the same random values using the RNG."""
    rng: np.random.Generator = field(init=False)
    """The RNG used for sampling the Car refueling delay time values from a normal dist."""

    def __post_init__(self, rng_seed: InitVar[int | None]):
        self.rng = np.random.default_rng(rng_seed)

    def __repr__(self) -> str:
        return f"""GasStation(
                        is_available        = {self.is_available},
                        awaiting_init_ack   = {self.awaiting_initial_ack}
                        car_queue           = {[f'ID={car.ID} | no_gas={car.no_gas} | refuel_delay={refuel_delay}' for car, refuel_delay in self.car_queue]},
                        reusable_query      = {self.reusable_query},
                        received_ack        = {self.received_ack},
                        polling_delay_time  = {self.polling_delay_time},
                        next_car_delay_time = {self.next_car_delay_time})
"""


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
        # If the component is available, THEN the non-refuel delay timers are GUARANTEED to currently be INFINITY.
        # Else, other timers MUST take precedence, so assume refuel delay to be INFINITY.
        shortest_refuel_delay: float = INFINITY
        if self._is_available():
            shortest_refuel_delay = self._get_car_queue_elem_shortest_refuel()[1]   # May or may not be 0.0s

        # Always EXACTLY ONE of the following timers is finite, the rest are infinite.
        return min(shortest_refuel_delay,
                   self.state.polling_delay_time,
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

        # A QueryAck induces one of two possible behaviors
        #   1) do Query polling
        #   2) let new Car leave the gas station after QueryAck.t_until_dep
        elif self.Q_rack in inputs:
            query_ack: QueryAck = inputs[self.Q_rack]
            final_ack: QueryAck | None = None
            rejected_ack = not self.state.receive_ack(query_ack)

            if self._is_awaiting_init_ack():
                self._set_awaiting_init_ack(False)
                # Polling initialization condition reached ...
                if query_ack.t_until_dep == INFINITY:
                    output_car: Car = self._get_car_queue_elem_shortest_refuel()[0]
                    self.state.start_polling(output_car)
                    self.state.received_ack = query_ack     # Purely aesthetic for the output trace
                # Initial QueryAck is finite
                else:
                    final_ack = query_ack
            # Will ignore QueryAcks if not awaiting initial ack and not polling
            elif rejected_ack:
                return self.state
            # Polling termination condition reached ...
            elif self.state.is_ack_finite():
                final_ack = self.state.stop_polling()

            # Finite QueryAck received ...
            if final_ack is not None:
                output_car: Car = self._get_car_queue_elem_shortest_refuel()[0]
                output_car.no_gas = False
                # Start Car output timer
                self.state.next_car_delay_time = final_ack.t_until_dep

        return self.state
    
    def outputFnc(self):
        """May NOT edit state."""
        
        # IF available, the outputFnc is reached when a refuel delay
        # timer in the car queue reaches 0.0s.
        if self._is_available():
            return {
                self.Q_send: Query(self._get_car_queue_elem_shortest_refuel()[0].ID)
            }

        # ELIF polling, the outputFnc is reached when the observ delay
        # timer reaches 0.0s
        elif self.state.is_polling():
            return {
                self.Q_send: self.state.get_query()
            }

        # ELSE car output, the outputFnc is reached when the next car delay
        # timer reaches 0.0s
        return {
            self.car_out: self._get_car_queue_elem_shortest_refuel()[0]
        }
        
    def intTransition(self):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.timeAdvance())

        # After sending the initial/non-polling Query ...
        if self._is_available():
            # Prevent further initial/non-polling Queries
            self._set_available(False)
            self._set_awaiting_init_ack(True)

        # After sending a subsequent/polling Query ...
        elif self.state.should_poll_again():
            self.state.continue_polling(self.observ_delay)

        # After outputting a Car ...
        elif self.state.next_car_delay_time == 0.0:
            self.state.car_queue.pop(0)
            self._set_available(True)
            # Give precedence to refuel timers, so set all non-refueling timers to INFINITY
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

    def _is_awaiting_init_ack(self) -> bool:
        """Check whether we are awaiting the initial QueryAck."""
        return self.state.awaiting_initial_ack
    
    def _set_awaiting_init_ack(self, sent_initial: bool) -> None:
        """Set whether we are awaiting the initial QueryAck."""
        self.state.awaiting_initial_ack = sent_initial

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
        if self._queue_is_empty():
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
        # mex(0.0, timer) not needed for following timers, all are INFINITY except for the running/relevant timer
        self.state.update_polling_timers(time_delta)
        self.state.next_car_delay_time -= time_delta
