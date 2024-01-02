
from tests.helpers import Scheduler, CDEVS

from components.generator import uuid
from components.roadsegment import RoadSegment
from components.messages import Car, Query, QueryAck
from other.ping_pong_multi import PingPongMulti

from pypdevs.simulator import Simulator


"""
The Query polling of a RoadSegment happens when a Car
 has velocity 0.0. The added experiment enters a Car
 with velocity 0.0 and makes a PingPongMulti pong back
 QueryAcks with t_until_dep=inf a few times, so that
 the correct behavior of polling can manually be checked.

The experiment also manually schedules additional QueryAcks
 to arrive at the same time as the first QueryAck returned
 by the PingPongMulti with t_until_dep!=inf, to test the
 velocity update priority implementation lightly.

Lastly, an incoming Query is manually scheduled to arrive
to test if the t_until_dep value is properly updated
by intTransition and extTransition calls or if it is
instead 'interrupted/prolonged' by transitions, causing
the Car to not truly remain in the RoadSegment for
exactly t_until_dep, but longer instead.
"""


model = CDEVS("model")
CAR_ID: uuid.UUID = uuid.uuid4()
car = Car(CAR_ID, 15, 5, 5, v=0)
car_scheduler = model.addSubModel(Scheduler("Car"+Scheduler.__name__, [
    (0, car),
]))
ack_scheduler = model.addSubModel(Scheduler("Ack"+Scheduler.__name__, [
    (1.1, QueryAck(0, t_until_dep=10.0, sideways=True)),           # Incorrect Car ID used, non-relevant QueryAck
    (1.1, QueryAck(CAR_ID, t_until_dep=1.0, sideways=True)),     # Correct Car ID used, relevant QueryAck
]))
query_scheduler = model.addSubModel(Scheduler("Query"+Scheduler.__name__, [
    # Neither receiving a Query nor sending a QueryAck in reply should 'interrupt' the t_until_dep timer
    (1.9, Query(123321)),
]))
rs = model.addSubModel(RoadSegment(RoadSegment.__name__, 10, 10))
ppm = model.addSubModel(PingPongMulti(
    PingPongMulti.__name__,
    t_until_dep=5.0,
    pong_delay=0.2,
    first_x_inf=3,
    do_max=True))
model.connectPorts(car_scheduler.output, rs.car_in)
model.connectPorts(ack_scheduler.output, rs.Q_rack)
model.connectPorts(query_scheduler.output, rs.Q_recv)
model.connectPorts(rs.Q_send, ppm.inp)
model.connectPorts(ppm.out, rs.Q_rack)

sim = Simulator(model)
sim.setClassicDEVS()
sim.setVerbose()
sim.simulate()