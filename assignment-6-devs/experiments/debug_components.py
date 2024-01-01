from pypdevs.simulator import Simulator





SM = 'sm'   # sidemarker
CL = 'cl'   # collector
GN = 'gn'   # generator
GS = 'gs'   # gasstation
test_names = [
    SM, CL, GN, GS
]

test_name = 'test'
test_name = test_names[3]



match test_name:
    case 'sm':
        from components.sidemarker import SideMarker
        
        from tests.helpers import *
        from components.messages import *


        model = CDEVS("model")
        sc = model.addSubModel(Scheduler("sc", [
            (1, QueryAck(1, 0.0)),
            (2, QueryAck(2, 0.0)),
            (3, QueryAck(3, 0.0))
        ]))
        sm = model.addSubModel(SideMarker("sm"))
        model.connectPorts(sc.output, sm.mi)

        sim = Simulator(model)
        sim.setTerminationTime(10)
        sim.setClassicDEVS()
        sim.setVerbose()          # Simulator tracks all events/state changes?

        sim.simulate()

    case 'cl':
        from components.collector import Collector
        
        from tests.helpers import *
        from components.messages import *


        model = CDEVS("model")
        sc = model.addSubModel(Scheduler("sc", [
            (1, Car(1, 15, 5, 5, 1)),
            (5, Car(2, 15, 5, 5, 2)),
            (10, Car(3, 15, 5, 5, 3)),
            (15, Car(4, 15, 5, 5, 4)),
        ]))
        sm = model.addSubModel(Collector("cl"))
        model.connectPorts(sc.output, sm.car_in)

        sim = Simulator(model)
        sim.setTerminationTime(20)
        sim.setClassicDEVS()
        sim.setVerbose()          # Simulator tracks all events/state changes?

        sim.simulate()
    
    case 'gn':
        from tests.helpers import *
        from components.generator import Generator

        limit: int = 4
        model = CDEVS("model")
        pp = model.addSubModel(PingPong("A"))
        gen = model.addSubModel(Generator("GENERATOR", 5, 7, 10, 20, ["E"], limit=limit))
        cl = model.addSubModel(TestCollector("cl"))
        model.connectPorts(gen.Q_send, pp.inp)
        model.connectPorts(pp.out, gen.Q_rack)
        model.connectPorts(gen.car_out, cl.inp)

        sim = Simulator(model)
        sim.setClassicDEVS()
        sim.setVerbose()
        sim.simulate()

        cars = [x[1] for x in cl.state["data"]]

    case 'gs':
        from other.ping_pong_multi import PingPongMulti
        from tests.helpers import *
        from components.gasstation import GasStation

        n: int = 2#1000

        model = CDEVS("model")
        pre_cars = [(x, Car(x, 15, 5, 5, v=15, departure_time=x, no_gas=True)) for x in range(n)]
        pre_sim_gas_total: int = sum([car.no_gas for _, car in pre_cars])

        sc = model.addSubModel(Scheduler(Scheduler.__name__, pre_cars))
        pp = model.addSubModel(PingPongMulti(PingPongMulti.__name__, t_until_dep=5.0, pong_delay=0.2, first_x_inf=3))
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

        times = [x[0] - x[1].departure_time for x in cl.state["data"]]
        cars = [x[1] for x in cl.state["data"]]

        print("\n=== STATS ===\n")
        print("set(c.ID for c in cars) == set(x for x in range(n))   : ",set(c.ID for c in cars) == set(x for x in range(n)))

        print(set(c.ID for c in cars))
        print(set(x for x in range(n)))
        print()
        print()
        print()

        avg_time = sum(times) / len(times)
        print("avg_time : ", avg_time)
        print("580 < avg_time < 620   : ", 580 < avg_time < 620)
        print("min(times) >= 120      : ", min(times) >= 120)
        print("sum([car.no_gas for car in cars]) (expect 0) :\n", "\tpre-sim : ", pre_sim_gas_total, "\n\tpost-sim: ", sum([car.no_gas for car in cars]))


    case 'test':
        from other.ping_pong_multi import PingPongMulti
        from tests.helpers import CDEVS, Scheduler
        from components.messages import Query

        model = CDEVS("model")
        sc = model.addSubModel(Scheduler(Scheduler.__name__, [
            (t / 20, Query(t))
            for t in range(6)
            
            
        ] + [
            (20, Query(20)),
            (20, Query(21)),
        ]))
        ppm = model.addSubModel(PingPongMulti(PingPongMulti.__name__))
        model.connectPorts(sc.output, ppm.inp)

        sim = Simulator(model)
        # sim.setTerminationTime(10)
        sim.setClassicDEVS()
        sim.setVerbose()          # Simulator tracks all events/state changes?

        sim.simulate()

print("\n"*4, "=== DONE ===\n")
