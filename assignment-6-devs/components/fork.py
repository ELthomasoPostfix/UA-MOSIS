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

    def extTransition(self, inputs):
        """May edit state."""
        return self.state


    def intTransition(self):
        """May edit state."""
        return self.state