from pypdevs.simulator import Simulator

from other.ping_pong_multi import PingPongMulti
from tests.helpers import CDEVS, Scheduler, TestCollector

from components.messages import Car
from other.gasstation_realistic_polling import GasStation


"""
Running this script a few timer will eventually result in an AssertionError.
The timeAdvance() method of the PingPongMulti class will return a negative
value!!!

Note, this problem also occurs with the supermarket.py script made during the
turorial, it seems? Run it enough times, and the last line of its output will
read something similar to:

    DEVS Exception: Negative time advance in atomic model 'market.store' with value -1.8894358316271855 at time 66.012627

Also, this experiment is a showcase of a GasStation implementation that makes use
of realistic polling. By 'realistic polling', we mean the following: Suppose that the
roundtrip time for a Query is 2s, then the following trace may occur:
at global time 0.0s     GasStation sends Query 1
at global time 1.0s     GasStation sends Query 2
at global time 2.0s     GasStation receives QueryAck 1
at global time 2.0s     GasStation sends Query 3
at global time 3.0s     GasStation receives QueryAck 2
at global time 4.0s     GasStation receives QueryAck 3

This is as opposed to a simplified polling behavior:
at global time 0.0s     GasStation send Query 1
at global time 2.0s     GasStation receives Query 1
at global time 3.0s     GasStation send Query 2
at global time 5.0s     GasStation receives Query 2
at global time 6.0s     GasStation send Query 3
at global time 8.0s     GasStation receives Query 3


"""



n: int = 2#1000
DO_MAX_FOR_EXT: bool = True
# DO_MAX_FOR_EXT = False





model = CDEVS("model")
pre_cars = [(x, Car(x, 15, 5, 5, v=15, departure_time=x, no_gas=True)) for x in range(n)]
pre_sim_gas_total: int = sum([car.no_gas for _, car in pre_cars])

sc = model.addSubModel(Scheduler(Scheduler.__name__, pre_cars))
pp = model.addSubModel(PingPongMulti(
    PingPongMulti.__name__,
    t_until_dep = 5.0,
     pong_delay = 0.2,
    first_x_inf = 3,
         do_max = DO_MAX_FOR_EXT,
))
gs = model.addSubModel(GasStation(GasStation.__name__))
cl = model.addSubModel(TestCollector(TestCollector.__name__))
model.connectPorts(sc.output, gs.car_in)
model.connectPorts(gs.Q_send, pp.inp)
model.connectPorts(pp.out, gs.Q_rack)
model.connectPorts(gs.car_out, cl.inp)

sim = Simulator(model)
sim.setClassicDEVS()
sim.setVerbose()
sim.simulate()