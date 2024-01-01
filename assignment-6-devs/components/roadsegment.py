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
    previous_v_update_time: float = INFINITY
    """The amount of time that passed since the current car's velocity was last updated."""
    v_updates: List[float] = field(default_factory=list)
    """The list of car possible velocity updates collected at the exact same time."""
    v_apply_updates_time: float = INFINITY      # Is either 0.0s or INFINITY
    """A timer to trigger the application of one of the collected velocity updates, to the car."""

    t_until_dep: float = 0.0
    """The time until the current Car (i.e., the first one in cars_present) leaves the RoadSegment. If the Car's velocity is 0, this value is infinity. If no Car is present, this value is 0."""
    incoming_queries_queue: List[Tuple[Query, float]] = field(default_factory=list)

    """The FIFO queue of incoming/external Query events. Each queue element is a tuple containing (Query, remaining observe delay time). Because index 0 is the head of the queue, the remaining observe delay time will naturally be ordered in ascending order."""
    next_car_Ack: QueryAck | None = None
    """The QueryAck that signifies that the next car may be sent to the car_out port."""
    observ_delay_time_outgoing: float = INFINITY  # Is in  [ 0.0s, self.observ_delay ] U INFINITY
    """A delay variable used to decide when the next Query should be output, after some Car entered the RoadSegment. This timer is distinct from the observ delay timers kept for each incoming Query. This timer is used for outgoing Query events."""

    # Statistics
    n_enter: int = 0
    """The number of cars that have entered this RoadSegment. See the car_in port description."""
    n_crash: int = 0
    """The number of crashes that have occurred in this RoadSegment. See the car_in port description."""

    def __repr__(self) -> str:
        return f"""RoadSegment(
                        cars                = {[f'ID={car.ID} | v={car.v} | v_pref={car.v_pref}' for car in self.car_queue]},
                        remaining_x         = {self.is_available},
                        t_until_dep         = {self.t_until_dep}
                        incoming_queries_q  = {[f'ID={query.ID} | rem_observ_delay={rem_observ_delay}' for query, rem_observ_delay in self.car_queue]},
                        observ_delay_out    = {self.observ_delay_time_outgoing},
                        n_enter             = {self.n_enter},
                        n_crash             = {self.n_crash},
"""


class RoadSegment(AtomicDEVS):
    """Represents a small stretch of road that can only contain a single Car.
    
    When multiple Cars are on a RoadSegment, we assume the Cars crashed into each other.
    """

    # TODO: L can be default to 5.0?
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
        self.Q_send = self.addOutPort("Q_send")
        """Sends a Query as soon as a new Car arrives on this RoadSegment (if there was no crash). Additionally, a Query is sent every observ_delay time if the Car's v equals 0."""
        self.Q_sack = self.addOutPort("Q_sack")
        """Replies a QueryAck to a Query. The QueryAck's t_until_dep equals the remaining time of the current Car on the RoadSegment (which can be infinity if the Car's velocity is 0). If there is no Car, t_until_dep equals zero. The QueryAck's lane is set w.r.t. the RoadSegment's lane; and the QueryAck's sideways is set to be false here."""

    def timeAdvance(self):
        """May NOT edit state."""

        # The closest action that will need to be taken ([1] acknowledging Query, [2] sending Query, [3] re-computing velocity)
        return min(self._get_shortest_observ_delay_incoming(),
                   self.state.observ_delay_time_outgoing,
                   self.state.v_apply_updates_time)

    def extTransition(self, inputs):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.elapsed)

        # Enqueue an incoming Query event on the FIFO queue
        if self.Q_recv in inputs:
            query: Query = inputs[self.Q_recv]
            self.state.incoming_queries_queue.append((query, self.observ_delay))

        # A Car enters the RoadSegment
        elif self.car_in in inputs:
            new_car: Car = inputs[self.car_in]
            self.car_enter(new_car)

        # See GasStation Q_rack extTransition
        elif self.Q_rack in inputs:
            query_ack: QueryAck = inputs[self.Q_rack]
            self.state.next_car_Ack = query_ack

            current_car: Car = self._get_current_car()
            if current_car is None:
                return self.state

            # Collect & update time since previous velocity update
            t_no_coll: float = query_ack.t_until_dep


            def clamp_speed(car: Car, v_target: float):
                """Return the new speed that the *car* would like to attain if possible.

                This method implements the acceleration or deceleration of the *car*'s
                speed towards its v_pref.

                :return: The desired new speed
                """
                # Accel/Decel to v_target according to dv_pos_max/dv_neg_max
                if car.v < v_target:
                    speed_max_accel: float = car.v + car.dv_pos_max * self.state.previous_v_update_time
                    return min(speed_max_accel, v_target, self.v_max)
                elif car.v > v_target:
                    speed_max_decel: float = car.v - car.dv_neg_max * self.state.previous_v_update_time
                    return max(speed_max_decel, v_target, 0.0)
                else:
                    return v_target

            if not query_ack.sideways:
                v_new = clamp_speed(current_car, current_car.v_pref)
                t_exit = self.state.remaining_x / v_new
                # Car will arrive at next RoadSegment while it is still occupied by another Car
                # Collision will occur, slow down to the minimum speed such that collision is avoided
                if t_no_coll > t_exit:
                    v_new = self.state.remaining_x / t_no_coll
                # No collision, keep v_new as is
                else:
                    pass
            else:
                if not query_ack.priority:
                    # Decelerate to zero as fast as possible
                    # i.e. the target speed is 0.0
                    v_new = 0.0
                else:
                    v_new = current_car.v_pref

            updated_car_v: float = clamp_speed(current_car, v_new)
            self.state.v_updates.append(updated_car_v)
            self.state.v_apply_updates_time = 0.0
        return self.state

    def outputFnc(self):
        """May NOT edit state."""

        # TODO calling _should_sack() or _should_send() in outputFnc does not work!!!!
        # TODO calling _should_sack() or _should_send() in outputFnc does not work!!!!
        # TODO calling _should_sack() or _should_send() in outputFnc does not work!!!!

        # Should send QueryAck
        if (self._get_shortest_observ_delay_incoming() - self.timeAdvance()) == 0.0:
            query: Query = self.state.incoming_queries_queue[0][0]
            # TODO is this t_until_dep given to the QueryAck correctly calculated at this moment????
            #   ==> See calculate_t_until_dep()
            #   ==> But why is there a t_until_dep in state then???
            return {
                self.Q_sack: QueryAck(query.ID, self.state.t_until_dep, self.lane, sideways=False)
            }

        elif self._is_query_sent():
            return {
                self.Q_send: Query(self._get_current_car().ID)
            }

        return {
        }

    def intTransition(self):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.timeAdvance())

        # (1) After sending a QueryAck in reply to a Query arriving ...
        if self._is_ack_sent():
            self.state.incoming_queries_queue.pop(0)

        # (2) After sending a Query in response to a Car arriving ...
        elif self._is_query_sent():
            self.state.observ_delay_time_outgoing = INFINITY

        # (3) After sending a Car to the Car output port ...
        # elif ...
        #     self.state.previous_v_update = INFINITY

        # (4) After collecting possible velocity updates from
        # external QueryAck events ...
        elif self.state.v_apply_updates_time == 0.0:
            applied_velocity: float = max(self.state.v_updates)
            self._get_current_car().v = applied_velocity
            self.state.v_updates.clear()
            # Allow independent velocity updates
            self.state.v_apply_updates_time = INFINITY

        return self.state

    def car_enter(self, car: Car) -> None:
        """Handles all the logic of a *car* entering the RoadSegment.
        
        Can be called to pre-fill the RoadSegment with a Car.
        """
        # Handle collision
        collision = self._is_car_present()

        self.state.n_enter += 1
        self.state.cars_present.append(car)

        if collision:
            self.state.n_crash += 1
            self.state.cars_present = []

            return

        # Immediately send Query
        self.state.previous_v_update_time = 0.0
        self.state.observ_delay_time_outgoing = 0.0

    def _is_query_received(self) -> bool:
        """Check whether any incoming Query is currently being processed."""
        return len(self.state.incoming_queries_queue) > 0

    def _is_car_present(self) -> bool:
        """Check whether any Car is present in the RoadSegment."""
        return len(self.state.cars_present) > 0

    def _get_shortest_observ_delay_incoming(self) -> float:
        """Get the shortest remaining observe delay associated with any incoming Query.

        If there are no incoming Queries, then the output defaults to INFINITY.
        """
        if self._is_query_received():
            return self.state.incoming_queries_queue[0][1]
        return INFINITY

    def _is_ack_sent(self) -> bool:
        """Check whether a QueryAck should be sent on the Q_sack port in response to the expiration of an observ delay timer for an incoming Query, according to the current state."""
        return self._get_shortest_observ_delay_incoming() == 0.0

    def _is_query_sent(self) -> bool:
        """Check whether a Query should be sent on the Q_send port in response to the expiration of the query delay timer, according to the current state."""
        return self.state.observ_delay_time_outgoing == 0.0

    def _get_current_car(self) -> Car | None:
        """Get the (frontmost) Car that is currently travelling down the RoadSegment.
        
        If no Car is present, return None instead.
        """
        if self._is_car_present():
            return self.state.cars_present[0]
        return None

    def calculate_t_until_dep(self) -> float:
        """Calculate t_until_dep for the current Car. Defaults to 0.0 is there is no current Car."""
        current_car: Car = self._get_current_car()

        # RoadSegment is unoccupied
        if current_car is None:
            return 0.0
        # Car is stationary --> blocks RoadSegment
        if current_car.v == 0.0:
            return INFINITY

        # velocity = distance / time   ==>   time = distance / velocity
        remaining_time: float = self.state.remaining_x / current_car.v

        return self._clamp(remaining_time, 0.0, self.v_max)

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
        # mex(0.0, timer) not needed for following timers, all are INFINITY except for the running/relevant timers
        self.state.observ_delay_time_outgoing -= time_delta
        self.state.previous_v_update_time += time_delta
