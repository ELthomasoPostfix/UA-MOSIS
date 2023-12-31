import unittest

from tests.helpers import *

from components.generator import uuid
from components.roadsegment import RoadSegment
from components.messages import *

from pypdevs.simulator import Simulator

model = CDEVS("model")
car = Car(uuid.uuid4(), 15, 5, 5, v=15)
sc1 = model.addSubModel(Scheduler("sc1", [(2, car)]))
sc2 = model.addSubModel(Scheduler("sc2", [(2.1, QueryAck(car.ID, 0.0))]))
rs = model.addSubModel(RoadSegment("rs", 10, 10))
cl = model.addSubModel(TestCollector("cl"))
model.connectPorts(sc1.output, rs.car_in)
model.connectPorts(sc2.output, rs.Q_rack)
model.connectPorts(rs.car_out, cl.inp)
cls = model.addSubModel(TestCollector("cls"))
model.connectPorts(rs.Q_send, cls.inp)

sim = Simulator(model)
sim.setClassicDEVS()
sim.setVerbose()
sim.simulate()

# model = CDEVS("model")
# sc1 = model.addSubModel(Scheduler("sc1", [(2, Car(1, 15, 5, 5, v=15))]))
# sc2 = model.addSubModel(Scheduler("Asc2", [(3, QueryAck(1, 0.0)), (3, QueryAck(1, 0.5, sideways=True))]))
# rs = model.addSubModel(RoadSegment("Brs", 30, 15))
# cl = model.addSubModel(TestCollector("cl"))
# model.connectPorts(sc1.output, rs.car_in)
# model.connectPorts(sc2.output, rs.Q_rack)
# model.connectPorts(rs.car_out, cl.inp)
#
# sim = Simulator(model)
# sim.setClassicDEVS()
# sim.setVerbose()
# sim.simulate()

# self.assertEqual(cl.get_data(0)[0], 4.5)
# self.assertEqual(cl.get_data(0)[1].v, 10)
