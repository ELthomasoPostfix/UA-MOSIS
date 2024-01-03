from pypdevs.simulator import Simulator
from pypdevs.DEVS import CDEVS

from tests.helpers import *

from components.crossroads import CrossRoadSegment


# #
#     ID: UUID | int
#     """ A unique identifier to uniquely distinguish between cars."""
#     v_pref: float
#     """ The preferred velocity of the car. This is the velocity the car tries to obtain whenever possible."""
#     dv_pos_max: float
#     """ The maximal amount of acceleration possible for this Car on a single RoadSegment. Notice that this is not actually a velocity, but more of a velocity delta. Feel free to choose your own values, but 28 is a good suggestion."""
#     dv_neg_max: float
#     """ The maximal amount of deceleration possible for this Car on a single RoadSegment. Notice that this is not actually a velocity, but more of a velocity delta. Feel free to choose your own values, but 21 is a good suggestion."""
#     departure_time: float = 0.0
#     """ The (simulation) time at which the Car is created. This value is set afterwards, by the Generator."""
#     distance_traveled: float = 0.0
#     """ The total distance that the Car has traveled. This value is updated during simulation."""
#     v: float = None     # Default value None, so we can default to v_pref
#     """ The current velocity. By default, it is initialized to be the same as v_pref, but may change during the simulation. This value is used for all the distance computations etc."""
#     no_gas: bool = False
#     """ Indicator that the Car needs gas. Will be used later in the assignment."""
#     destination: str = ""
#     """ The target destination of the Car. This will help for path planning etc in a more detailed library. Later on in the assignment, this value will be used for CrossRoads."""


model = CDEVS("crossroads")
sc1 = model.addSubModel(Scheduler("gen", [
    (2, Car(ID=1, v_pref=15, dv_pos_max=5, dv_neg_max=5, v=15, destination="R")),
]))
sc2 = model.addSubModel(Scheduler("cr_seg_prev", [
    (2, Car(ID=3, v_pref=15, dv_pos_max=5, dv_neg_max=5, v=15, destination="R")),
    # (6, Car(ID=5, v_pref=15, dv_pos_max=5, dv_neg_max=5, v=15, destination="R"))
]))
rs = model.addSubModel(CrossRoadSegment("rs", L=10, v_max=15, destinations=["R"]))

cl1 = model.addSubModel(TestCollector("cl1"))
cl2 = model.addSubModel(TestCollector("cl2"))

model.connectPorts(sc1.output, rs.car_in)
model.connectPorts(sc2.output, rs.car_in_cr)
model.connectPorts(rs.car_out, cl1.inp)
model.connectPorts(rs.car_out_cr, cl2.inp)

sim = Simulator(model)
sim.setClassicDEVS()
sim.simulate()


model = CrossRoadSegment("crossroad_segment")
simulator = Simulator(model)

simulator.setTerminationTime(1000)
simulator.setClassicDEVS()
simulator.setVerbose()

simulator.simulate()
