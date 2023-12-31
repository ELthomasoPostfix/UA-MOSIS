from dataclasses import dataclass
from typing import Tuple

from pypdevs.infinity import INFINITY

from components.messages import Car, Query, QueryAck



@dataclass
class QueryPollingState:
    """A parent class for states that require Query polling behavior.

    The strict call order and frequency of methods on this class' interface is as follows:
    1) start_polling(Car)            : exactly once
    2) in any order:
        2.a) continue_polling(float) : any amount of times
        2.b) receive_ack(QueryAck)   : any amount of times
    3) stop_polling()                : exactly once
    """

    reusable_query: Query | None = None
    """The Query to re-use for polling."""
    received_ack: QueryAck | None = None
    """The QueryAck received from polling."""
    polling_delay_time: float = INFINITY
    """A timer to keep track of when the next query should be output / sent to the Query output port."""

    def start_polling(self, next_car: Car) -> None:
        """Adjust the system state so that polling starts immediately.

        This method should be called at most once before the
        `reset_polling_state()` method is called.
        """
        assert not self._is_query_stored(), f"A {self.__class__.__name__} may not overwrite a reusable Query by generating a new one. The state must be reset first. See `reset_polling_state()`."

        # The same Query object should be used to poll until a positive QueryAck is received and
        # the related Car is sent to the Car output port.
        self.reusable_query = Query(next_car.ID)
        # Immediately poll with a Query initially
        self.continue_polling(poll_delay=0.0)

    def continue_polling(self, poll_delay: float) -> None:
        """Adjust the system state so that the next polling event happens in *poll_delay* seconds."""
        # Pattern 3: multiple timers,
        # set 'irrelevant' timers to INFINITY so that the sole 'relevant' timer has precedence.
        self._set_poll_delay_time(poll_delay)

    def receive_ack(self, query_ack: QueryAck) -> bool:
        """Receive a QueryAck and store it.
        
        The given *query_ack* is ignored in the following cases:
        * Polling is NOT in progress (see `is_polling()` and `start_polling(Car)`)
        * The *query_ack*'s ID does NOT match that of the stored Query's ID.

        The ignoring of QueryAcks when not polling can be used to ignore extraneous
        QueryAcks that arrive after the polling termination condition has been reached.
        Call `stop_polling()` to do so.

        :return: True if *query_ack* was stored successfully and False if it was ignored.
        """
        if not self.is_polling():
            return False

        # Ignore received QueryAck, it was meant for another DEVS component
        if query_ack.ID != self.reusable_query.ID:
            return False

        self.received_ack = query_ack
        return True

    def update_polling_timers(self, time_delta: float) -> None:
        """Update the polling timers based on the *time_delta*.

        This works for both `extTransition()` and `intTransition()` and
        may be called at any moment.
        """
        # mex(0.0, timer) not needed for following timers, all are INFINITY except for the running/relevant timer
        self._decrease_poll_delay_time(time_delta)

    def stop_polling(self) -> QueryAck:
        """Reset the polling state to its initial state values.
        
        Returns the final QueryAck so that it can be used to make cleanup
        changes to the other component state members.

        :return: The final QueryAck.
        """
        final_ack: QueryAck = self.received_ack
        self.reusable_query = None
        self.received_ack = None
        # Pattern 3: multiple timers,
        # all timers are initially 'irrelevant', so set them all to INFINITY.
        self._set_poll_delay_time(INFINITY)
        return final_ack

    def is_polling(self) -> bool:
        """Check whether polling is currently in progress."""
        return self._is_query_stored()

    def should_poll_again(self) -> bool:
        """Check whether a Query should be sent / whether a poll should happen."""
        return self.polling_delay_time == 0.0

    def get_query(self) -> Query | None:
        """Get the reusable Query object that should be used to poll. Returns None if there is no such Query."""
        return self.reusable_query

    def is_ack_received(self) -> bool:
        """Check whether a QueryAck has been received/is currently stored."""
        return self.received_ack is not None
    
    def is_ack_inf(self) -> bool:
        """Check whether the QueryAck.t_until_dep value == INFINITY.
        
        If no QueryAck is currently stored, defaults to False.
        """
        if self.is_ack_received():
            return self.received_ack.t_until_dep == INFINITY
        return False

    def is_ack_finite(self) -> bool:
        """Check whether the QueryAck.t_until_dep value != INFINITY.
        
        If no QueryAck is currently stored, defaults to False.
        """
        if self.is_ack_received():
            return self.received_ack.t_until_dep != INFINITY
        return False


    ##############################
    #   PRIVATE HELPER METHODS   #
    ##############################

    def _is_query_stored(self) -> bool:
        """Check whether the Query object to use in polling has been stored."""
        return self.reusable_query is not None

    def _set_poll_delay_time(self, new_delay: float) -> None:
        """Set the remaining delay time until a Query should be sent / until a poll should happen.
        
        The *new_delay* MUST be greater than or equal to 0.0.
        """
        assert new_delay >= 0.0, f"Cannot set the poll delay timer to a negative value: got {new_delay}, expected >= 0.0"
        self.polling_delay_time = new_delay

    def _decrease_poll_delay_time(self, decrease: float) -> None:
        """Decrease the remaining delay time until a Query should be sent / until a poll should happen
        by the *decrease* amount.
        
        The remaining delay time after decreasing MUST be greater than or equal to 0.0.
        """
        new_delay: float = self.polling_delay_time - decrease
        assert new_delay >= 0.0, f"Cannot decrease the poll delay timer to a negative value: got {new_delay} = {self.polling_delay_time} - {decrease}, expected >= 0.0"
        self._set_poll_delay_time(new_delay)
