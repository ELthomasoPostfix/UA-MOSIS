from pypdevs.DEVS import AtomicDEVS



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
