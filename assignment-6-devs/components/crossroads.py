from pypdevs.DEVS import CoupledDEVS

from components.roadsegment import RoadSegment



class CrossRoadSegment(RoadSegment):
    """Acts as if it were a part of a crossroads. I.e., this is a location where two roads merge and split at the same time.
    Combining multiple of these segments together results in a CrossRoad.

    Given that this block inherits from RoadSegment, all aspects discussed there are also applicable.
    """
    def __init__(self, block_name: str, L: float, v_max: float,
                 observ_delay: float = 0.1, priority: bool = False, lane: int = 0,
                 destinations: list = None):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        :param L: The length of the RoadSegment. Given that the average Car is about 5 meters in length, a good estimate value for L would therefore be 5 meters.
        :param v_max: The maximal allowed velocity on this RoadSegment.
        :param observ_delay: The time it takes to reply to a Query that was inputted. This value mimics the reaction time of the driver. We can increase the observ_delay to accomodate for bad weather situations (e.g., a lot of fog and/or rain). Defaults to 0.1.
        :param priority: Whether or not this RoadSegment should have priority on a merge with other road segments. Defaults to False.
        :param lane: Indicator of the lane this Roadsegment is currently part of. Defaults to 0.
        :param destinations: A list of destinations reachable when a car exits the crossroads at this location. This list will be initialized upon creation of the road map and should not be changed afterwards. It is used to make sure Cars exit the crossroads at the right time.
        """
        super(CrossRoadSegment, self).__init__(block_name=block_name, L=L, v_max=v_max,
                         observ_delay=observ_delay, priority=priority, lane=lane)

        self.destinations: list = destinations if destinations is not None else list()
        """A list of destinations reachable when a car exits the crossroads at this location. Is immutable, so its should NOT be part of the model state member."""



class CrossRoads(CoupledDEVS):
    """Represents a free-for-all n-way crossroads.
    
    The internal representation for a 4-way implementation is as shown in the assignment.
    For the sake of readability, the outer ports are here encoded using North (N), East (E), South (S), West (W);
    instead of using indexes. This same encoding is used to distinguish between the individual CrossRoadSegments in the image.
    """
    def __init__(self, block_name: str, destinations: list, L: float,
                 v_max: float, observ_delay: float):
        """
        :param block_name: The name for this model. Must be unique inside a (parent) Coupled DEVS.
        :param destinations: A list of lists of destinations for the CrossRoads. The amount of sub-lists indicates how many branches the CrossRoads has. Each sub-list is given to the CrossRoadSegments in order.
        :param L: The length of the individual CrossRoadSegments.
        :param v_max: The maximal allowed velocity on the CrossRoads.
        :param observ_delay: The observ_delay for the CrossRoadSegments.
        """
        super(CrossRoads, self).__init__(block_name)
