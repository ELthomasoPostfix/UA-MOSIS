from dataclasses import dataclass, field
from typing import List, Tuple

from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

from components.messages import Car, QueryAck, Query


class Priority:
    """The priority of different velocity updates within the same exact moment."""
    PNone: int = -1
    """Unassigned/Default priority"""
    P0: int = 0
    """Priority 0: car may go as fast as allowed by the road"""
    P1: int = 1
    """Priority 1: car may go as fast as allowed by the road AND collision speed"""
    P2: int = 2
    """Priority 2: car must go as slow as necessary"""

    @staticmethod
    def priority_to_str(priority: int):
        match priority:
            case Priority.PNone:
                return 'UNSET'
            case Priority.P0:
                return 'P0'
            case Priority.P1:
                return 'P1'
            case Priority.P2:
                return 'P2'
            case _:
                return 'UNKNOWN'


@dataclass
class RoadSegmentState:
    remaining_x: float
    """The remaining distance that the current Car (i.e., the first one in cars_present) should still travel on this RoadSegment."""
    cars_present: List[Car] = field(default_factory=list)
    """A list for all the Cars on this RoadSegment. Even though the existence of multiple Cars results in a collision, for extensibility purposes a list should be used."""
    v_current_priority_int: int = Priority.PNone
    """The 'priority int' associated with the current Car's velocity. This int is used to determine whether a velocity change due to a QueryAck is allowed to happen."""
    incoming_queries_queue: List[Tuple[Query, float]] = field(default_factory=list)
    """The FIFO queue of incoming/external Query events. Each queue element is a tuple containing (Query, remaining observe delay time). Because index 0 is the head of the queue, the remaining observe delay time will naturally be ordered in ascending order."""

    # Timers
    t_until_send_query: float = INFINITY  # Is in  [ 0.0s, self.observ_delay ] U INFINITY
    """A timer used to decide when the next Query should be output. This happens either after some Car entered the RoadSegment (send an initial Query) or when the Car's velocity is 0 (Query polling behavior). This timer is distinct from the observ delay timers kept for each incoming Query. This timer is used for outgoing Query events."""
    t_until_dep: float = 0.0  # Updated manually upon Car velocity updates
    """The time until the current Car (i.e., the first one in cars_present) leaves the RoadSegment. If the Car's velocity is 0, this value is infinity. If no Car is present, this value is 0."""

    # Statistics
    n_enter: int = 0
    """The number of cars that have entered this RoadSegment. See the car_in port description."""
    collisions: int = 0
    """The number of crashes that have occurred in this RoadSegment. See the car_in port description."""

    def __repr__(self) -> str:
        return f"""RoadSegment(
                        cars                = {[f'ID={car.ID} | v={car.v} | v_pref={car.v_pref} | dest={car.destination}' for car in self.cars_present]},
                        incoming_queries_q  = {[f'ID={query.ID} | rem_observ_delay={rem_observ_delay}' for query, rem_observ_delay in self.incoming_queries_queue]},
                        remaining_x         = {self.remaining_x},
                        v_curr_priority     = {Priority.priority_to_str(self.v_current_priority_int)}
                        t_until_dep         = {self.t_until_dep}
                        t_until_send_query  = {self.t_until_send_query},
                        n_enter             = {self.n_enter},
                        n_crash             = {self.collisions},
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

    def __repr__(self):
        return self.state.__repr__()

    def timeAdvance(self):
        """May NOT edit state."""

        # Car.v == 0.0, then t_until_send_query will ALWAYS be started.
        # ==> polling will happen when needed if t_until_send_query is
        #    always considered in the timeAdvance() output

        # No Car on RoadSegment, so t_until_dep does not contribute to timeAdvance()
        t_until_dep_time: float = self.state.t_until_dep
        if self._get_current_car() is None:
            t_until_dep_time = INFINITY

        # The closest action that will need to be taken ([1] acknowledging Query, [2] sending Query, [3] re-computing velocity)
        return min(self._get_shortest_observ_delay_incoming(),
                   self.state.t_until_send_query,
                   t_until_dep_time)

    def extTransition(self, inputs):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.elapsed)

        # A Car enters the RoadSegment
        if self.car_in in inputs:
            new_car: Car = inputs[self.car_in]
            self.car_enter(new_car)

        # Enqueue an incoming Query event on the FIFO queue
        elif self.Q_recv in inputs:
            query: Query = inputs[self.Q_recv]
            self.state.incoming_queries_queue.append((query, self.observ_delay))

        # See GasStation Q_rack extTransition
        # TODO: check lane number in QueryAck
        elif self.Q_rack in inputs:
            query_ack: QueryAck = inputs[self.Q_rack]

            current_car: Car = self._get_current_car()
            # TODO: In Fork, return self.state if query_ack.lane != car.no_gas
            # Ignore ALL QueryAcks that are not meant for this AtomicDEVS component.
            if current_car is None or current_car.ID != query_ack.ID:
                return self.state

            def clamp_speed(car: Car, v_target: float):
                """Return the new speed that the *car* would like to attain if possible.

                This method implements the acceleration or deceleration of the *car*'s
                speed towards its v_pref.

                :return: The desired new speed
                """
                # Accel/Decel to v_target according to dv_pos_max/dv_neg_max
                v: float
                if car.v < v_target:
                    speed_max_accel: float = car.v + car.dv_pos_max
                    v = min(speed_max_accel, v_target)
                elif car.v > v_target:
                    speed_max_decel: float = car.v - car.dv_neg_max
                    v = max(speed_max_decel, v_target)
                else:
                    v = v_target
                return self._clamp(v, 0.0, self.v_max)

            # Collect & update time since previous velocity update
            t_no_coll: float = query_ack.t_until_dep

            priority_int: int = Priority.P0

            if not query_ack.sideways:
                v_new = clamp_speed(current_car, current_car.v_pref)
                t_exit = self.state.remaining_x / v_new
                # Car will arrive at next RoadSegment while it is still occupied by another Car
                # Collision will occur, slow down to the minimum speed such that collision is avoided
                if t_no_coll > t_exit:
                    v_new = self.state.remaining_x / t_no_coll
                    priority_int = Priority.P1
                # No collision, keep v_new as is
                else:
                    pass
            else:
                if not self.priority:
                    if t_no_coll == 0.0:
                        # Keep driving as is
                        priority_int = Priority.P1

                        v_new = clamp_speed(current_car, current_car.v_pref)
                        t_exit = self.state.remaining_x / v_new
                        # Car will arrive at next RoadSegment while it is still occupied by another Car
                        # Collision will occur, slow down to the minimum speed such that collision is avoided
                        if t_no_coll > t_exit:
                            v_new = self.state.remaining_x / t_no_coll
                        else:
                            pass
                        # No collision, keep v_new as is
                    else:
                        # Decelerate to zero as fast as possible
                        # i.e. the target speed is 0.0
                        v_new = 0.0
                        priority_int = Priority.P2
                else:
                    v_new = current_car.v_pref

            updated_car_v: float = clamp_speed(current_car, v_new)

            if priority_int > self.state.v_current_priority_int:
                self.state.v_current_priority_int = priority_int
                current_car.v = updated_car_v
            elif priority_int == self.state.v_current_priority_int:
                current_car.v = (min if priority_int != 0 else max)(current_car.v, updated_car_v)
            else:
                pass

            # Consider changed Car velocity to update t_until_dep
            self.state.t_until_dep = self._calc_updated_t_until_dep()

            # After observ_delay, send Query (polling).
            # This check will catch any case of a Car having velocity 0.0 within the RoadSegment, because:
            #   1) If a Car enters and has 0.0 velocity, then an initial Query is sent.
            #      The QueryAck that follows results in a velocity update in the code
            #       above. If the updated velocity remains 0.0, then this will be caught here.
            #   2) If a Car enters and has > 0.0 velocity, then an initial Query is sent.
            #      The QueryAck that follows results in a velocity update in the code
            #      above. If the new velocity becomes 0.0, then this will be caught here.
            #
            # ==> If the updated velocity is:
            #   a) == 0.0, then polling will be started/restarted below
            #   b)  > 0.0, then polling will NOT be started/restarted below
            if current_car.v == 0.0:
                self.state.t_until_send_query = self.observ_delay

        return self.state

    def outputFnc(self):
        """May NOT edit state."""

        car = self._get_current_car()

        # (1) Send QueryAck to Q_sack port
        if self._should_send_ack(False):
            query: Query = self.state.incoming_queries_queue[0][0]
            true_t_until_dep: float = self._calc_updated_t_until_dep(self._calc_updated_remaining_x(self.timeAdvance()))
            return {
                self.Q_sack: QueryAck(query.ID, true_t_until_dep, self.lane, sideways=False, source=self.name)
            }

        # (2) Send Query to Q_send port (via initial query or polling)
        elif self._should_send_query(False):
            return {
                self.Q_send: Query(car.ID, source=self.name)
            }

        # (3) Send Car to car_out port
        elif self._should_car_depart(False):
            return {
                self.car_out: Car(
                    ID=car.ID, v_pref=car.v_pref, dv_pos_max=car.dv_pos_max, dv_neg_max=car.dv_neg_max,
                    departure_time=car.departure_time, distance_traveled=car.distance_traveled + self.L,
                    v=car.v, no_gas=car.no_gas, destination=car.destination, source=car.source
                )
            }

        return {
        }

    def intTransition(self):
        """May edit state."""
        # Pattern 3: multiple timers
        self._update_multiple_timers(self.timeAdvance())

        # (1) After sending a QueryAck in reply to a Query arriving ...
        if self._should_send_ack():
            self.state.incoming_queries_queue.pop(0)

        # (2) After sending a Query in response to a Car arriving ...
        elif self._should_send_query():
            self.state.t_until_send_query = INFINITY

        # (3) After sending a Car to the Car output port ...
        elif self._should_car_depart():
            self._car_exit()

        return self.state

    def car_enter(self, car: Car) -> None:
        """Handles all the logic of a *car* entering the RoadSegment.
        
        Can be called to pre-fill the RoadSegment with a Car.
        """
        # Handle collision
        collision = self._is_car_present()

        self.state.n_enter += 1

        if collision:
            self.state.collisions += 1
            # Evict the current Car as if it is exiting,
            # which resets the RoadSegment state
            self._car_exit()
            return

        # Do not append the colliding Car into the car_present
        # queue. Not doing so allows us to simply call the car
        # exit function.
        self.state.cars_present.append(car)

        # Immediately send Query
        self.state.t_until_send_query = 0.0

        # Initialize time until departed
        self.state.t_until_dep = self._calc_updated_t_until_dep()

    def _car_exit(self) -> None:
        """Handles all the logic of a *car* exiting the RoadSegment.

        The current implementation assumes the RoadSegment contains
        exactly one car at the time of calling.

        This method Should be called in case of a crash as well, to
        reset the RoadSegment state.
        """
        assert self._is_car_present(), f"Cannot handle Car exiting logic when no Car is present in the {self.__class__.__name__} instance."
        # Set 'irrelevant' timers to neutral INFINITY to signify them being off.
        # To be entirely safe, manually set ALL car-related timers to neutral values
        self.state.t_until_send_query = INFINITY
        self.state.t_until_dep = 0.0
        # Evict Car from queue
        self.state.remaining_x = self.L
        self.state.cars_present.pop(0)
        # Reset for completeness
        self.state.v_current_priority_int = Priority.PNone

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

    def _should_send_ack(self, timeUpdated: bool = True) -> bool:
        """Check whether a QueryAck should be sent on the Q_sack port in response to the expiration of an observ delay timer for an incoming Query."""
        return self._get_shortest_observ_delay_incoming() == (0.0 if timeUpdated else self.timeAdvance())

    def _should_send_query(self, timeUpdated: bool = True) -> bool:
        """Check whether the initial Query in response to a Car entering the RoadSegment or polling Query should be sent on the Q_send port."""
        return self.state.t_until_send_query == (0.0 if timeUpdated else self.timeAdvance())

    def _should_car_depart(self, timeUpdated: bool = True) -> bool:
        """Check whether the current Car should be sent on the car_out port."""
        return len(self.state.cars_present) and self.state.t_until_dep == (0.0 if timeUpdated else self.timeAdvance())

    def _get_current_car(self) -> Car | None:
        """Get the (frontmost) Car that is currently travelling down the RoadSegment.
        
        If no Car is present, return None instead.
        """
        if self._is_car_present():
            return self.state.cars_present[0]
        return None

    def _clamp(self, value: float, min_val: float, max_val: float) -> float:
        """Clamp the *value* to the fully closed interval `[ min_val, max_val ]`."""
        return min(max(value, min_val), max_val)

    def _update_multiple_timers(self, time_delta: float) -> None:
        """Update the internal countdown timers of the RoadSegment component, by decreasing them with *time_delta*.
        
        Implements the bulk of pattern 3: multiple timers.
        """
        # Update incoming Query observe delay timers
        self.state.incoming_queries_queue = [
            (query, max(0.0, observ_delay_remaining - time_delta))
            for query, observ_delay_remaining in self.state.incoming_queries_queue
        ]
        # mex(0.0, timer) not needed for following timers, all are INFINITY except for the running/relevant timers
        self.state.t_until_send_query -= time_delta

        # Update remaining_x and t_until_dep
        current_car: Car = self._get_current_car()
        if current_car is not None:
            # The Car travelled some distance since the previous update.
            self.state.remaining_x = self._calc_updated_remaining_x(time_delta)
            # Do not recalculate the t_until_dep value using the remaining_x / Car.v
            # metric, because this introduces floating point rounding errors.
            # These errors can cause the same Car to be output multiple times
            # out of the car_out port (or other such ports in DEVS that derive
            # from the RoadSegment DEVS).
            self.state.t_until_dep = max(0.0, self.state.t_until_dep - time_delta)

        # Velocity updates only need to consider the priority of
        # other velocity updates in the same exact moment.
        if time_delta != 0.0:
            self.state.v_current_priority_int = Priority.PNone

    def _calc_updated_remaining_x(self, time_delta: float):
        """Calculate the updated remaining_x based on the current Car velocity and the specified *time_delta* travel time.

        This method has NO side effects.
        """
        current_car: Car = self._get_current_car()
        if current_car is None:
            return self.state.remaining_x

        distance_travelled: float = time_delta * current_car.v
        return max(0.0, self.state.remaining_x - distance_travelled)

    def _calc_updated_t_until_dep(self, rem_x: float = None) -> float:
        """Update t_until_dep for the current velocity. Sets it to 0.0 if there is no Car.

        This method has NO side effects.
        """
        rem_x = self.state.remaining_x if rem_x is None else rem_x
        car: Car = self._get_current_car()
        if car is None:
            return 0.0
        else:
            return (rem_x / car.v) if car.v > 0.0 else INFINITY
