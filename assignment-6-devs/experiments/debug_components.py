from pypdevs.simulator import Simulator





SM = 'sm'   # sidemarker
CL = 'cl'   # collector
GN = 'gn'   # generator
test_names = [
    SM, CL, GN
]

test_name = test_names[2]



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


print("\n"*4, "=== DONE ===")
