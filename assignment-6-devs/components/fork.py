from components.roadsegment import RoadSegment



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
        self.car_out2 = self.addOutPort("car_out2")
        """Outputs the Car on this RoadSegment if it has traveled it completely. The Car's distance_traveled should be increased by L."""

    def outputFnc(self):
        """May NOT edit state."""

        output: dict = super(Fork, self).outputFnc()
        if self.car_out in output:
            car = output[self.car_out]
            if car.no_gas:
                output[self.car_out2] = car
                del output[self.car_out]
        return output
