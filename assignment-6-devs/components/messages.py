from dataclasses import dataclass, field
from uuid import UUID



@dataclass
class Car:
    """This is an event traveling passed between RoadSegments. It is used to model a car.
    
    Note that in this abstraction, somewhat counter-intuitively, the road segments are the
    "active" components, whereas the cars are "passive".
    This in contrast with an "agent based" abstraction where road segments would be the
    "passive" components and cars would be "active".
    
    This choice was made to allow for efficient simulation, when there are a limited number
    of road segments and a large number of cars.
    """

    ID: UUID | int
    """ A unique identifier to uniquely distinguish between cars."""
    v_pref: float
    """ The preferred velocity of the car. This is the velocity the car tries to obtain whenever possible."""
    dv_pos_max: float
    """ The maximal amount of acceleration possible for this Car on a single RoadSegment. Notice that this is not actually a velocity, but more of a velocity delta. Feel free to choose your own values, but 28 is a good suggestion."""
    dv_neg_max: float
    """ The maximal amount of deceleration possible for this Car on a single RoadSegment. Notice that this is not actually a velocity, but more of a velocity delta. Feel free to choose your own values, but 21 is a good suggestion."""
    departure_time: float = 0.0
    """ The (simulation) time at which the Car is created. This value is set afterwards, by the Generator."""
    distance_traveled: float = 0.0
    """ The total distance that the Car has traveled. This value is updated during simulation."""
    v: float = None     # Default value None, so we can default to v_pref
    """ The current velocity. By default, it is initialized to be the same as v_pref, but may change during the simulation. This value is used for all the distance computations etc."""
    no_gas: bool = False
    """ Indicator that the Car needs gas. Will be used later in the assignment."""
    destination: str = ""
    """ The target destination of the Car. This will help for path planning etc in a more detailed library. Later on in the assignment, this value will be used for CrossRoads."""
    source: str = ""
    """The source component that originally generated this Car."""

    def __post_init__(self, *args, **kwargs):
        if self.v is None:
            self.v = self.v_pref


@dataclass
class Query:
    """Represents the driver watching to the RoadSegment in front."""

    ID: UUID | int
    """The unique identifier of the Car that sends this Query."""
    source: str = ""
    """The source component that originally sent out this Query."""


@dataclass
class QueryAck:
    """Event that answers a Query. This is needed to actually obtain
    the information of the upcoming RoadSegment. The Query/QueryAck
    logic can therefore be seen as "polling".
    """

    ID: UUID | int
    """The unique identifier of the Car that queried this data."""
    t_until_dep: float
    """An estimate for the time until the upcoming RoadSegment is available again."""
    lane: int = 0
    """Indicates which lane the current RoadSegment applies to. If a Car wants to "change lanes" in a Fork, this value is used to identify which QueryAcks to take into account."""
    sideways: bool = False
    """Indicator that this QueryAck does not correspond to the RoadSegment in front, but rather another one the Car needs to keep track of. Defaults to false. Will be used later on in the assignment to allow for merges of RoadSegments."""
    source: str = ""
    """The source component that originally sent out this QueryAck."""
