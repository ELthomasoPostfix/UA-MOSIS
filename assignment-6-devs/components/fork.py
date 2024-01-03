from components.roadsegment import RoadSegment
from components.messages import Car



class Fork(RoadSegment):
    """
    Allows Cars to choose between multiple RoadSegments. This allows for a simplified form of "lane switching".
    For the sake of convenience of this assignment, the switching criteria is: output a Car over the car_out2 port if its no_gas member is true.
    
    Given that this block inherits from RoadSegment, all aspects discussed there are also applicable.
    """
    def __init__(self, block_name: str, L: float, v_max: float,
                 observ_delay: float = 0.1, priority: bool = False, lane: int = 0):
        super(Fork, self).__init__(block_name=block_name, L=L, v_max=v_max,
                         observ_delay=observ_delay, priority=priority, lane=lane)

        # Ports
        self.car_out2 = self.addOutPort("car_out2")
        """Outputs the Car on this RoadSegment if it has traveled it completely. The Car's distance_traveled should be increased by L."""

    def extTransition(self, inputs):
        """May edit state."""
        # IF Fork receives QueryAck for an incorrect lane,
        # OR if there is no Car in the Fork, then IGNORE the
        # incoming QueryAck, as it is not meant for the Fork.
        if self.Q_rack in inputs:
            # no_gas False  ==>  should goto car_out  / lane 0  ==>  ignore iff. QueryAck.lane == 1
            # no_gas True   ==>  should goto car_out2 / lane 1  ==>  ignore iff. QueryAck.lane == 0
            # Ignore iff. QueryAck.lane != int(no_gas)
            query_ack: QueryAck = inputs[self.Q_rack]
            current_car: Car = self._get_current_car()
            if current_car is None or query_ack.lane != current_car.no_gas:
                # Don't forget to update timers!!!
                self._update_multiple_timers(self.elapsed)
                return self.state

        # ELSE process the incoming event as normal.
        return super(Fork, self).extTransition(inputs)

    def outputFnc(self):
        """May NOT edit state."""

        output: dict = super(Fork, self).outputFnc()
        # If a Car is in the outputFnc() output of the RoadSegment,
        # then it must have travelled it completely
        if self.car_out in output:
            car: Car = output[self.car_out]
            if car.no_gas:
                output[self.car_out2] = car
                del output[self.car_out]
        return output
