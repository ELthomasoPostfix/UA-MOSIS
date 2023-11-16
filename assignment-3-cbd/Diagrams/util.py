from pyCBD.simulator import Simulator


def processData(cbd, field):
    data = cbd.getSignalHistory(field)
    print(data)
    return [x for x, _ in data], [y for _, y in data]


def runSimulation(cbd, duration, delta_t, fields):
    sim = Simulator(cbd)
    sim.setDeltaT(delta_t)
    sim.run(duration)

    return [processData(cbd, field) for field in fields]