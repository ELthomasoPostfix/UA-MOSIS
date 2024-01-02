from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.simulator import Simulator

from components.generator import Generator
from components.collector import Collector
from components.roadsegment import RoadSegment
from components.crossroads import CrossRoads


from other.road_stitcher import connect_segments, connect_crossroads


class NWayCrossroads(CoupledDEVS):
    """Represents a segment of road connecting a Generator to Collector, with a fork and gas station in between.
    """

    def __init__(self, block_name: str):
        """
        :param block_name: The name for this model. Must be unique inside a (parent) Coupled DEVS.
        """
        super(NWayCrossroads, self).__init__(block_name)

        num_connections = 4
        num_connecting_roads = 3

        # Components
        self.collectors = [self.addSubModel(Collector(f"col_{i}")) for i in range(num_connections)]
        destinations = [collector.name for collector in self.collectors]
        self.generators = [self.addSubModel(Generator(f"gen_{i}", IAT_min=0.5, IAT_max=1.5, v_pref_mu=5,
                                                      v_pref_sigma=1, destinations=destinations, limit=100))
                           for i in range(num_connections)]


        self.collector_segments = [
            [
                self.addSubModel(RoadSegment(f"col_{i}_seg_{j}", L=100, v_max=5, observ_delay=0.1))
                for j in range(num_connecting_roads)
            ]
            for i in range(num_connections)
        ]
        self.generator_segments = [
            [
                self.addSubModel(RoadSegment(f"gen_{i}_seg_{j}", L=100, v_max=5, observ_delay=0.1))
                for j in range(num_connecting_roads)
            ]
            for i in range(num_connections)
        ]

        crossroads_destinations = [ [f"col_{i}"] for i in range(num_connections)]

        self.crossroads = self.addSubModel(CrossRoads("cr", destinations=crossroads_destinations, L=100, v_max=5, observ_delay=0.1))


        crossroads_destinations = [ [f"col_{i}"] for i in range(num_connections)]

        self.crossroads = self.addSubModel(CrossRoads("cr", destinations=crossroads_destinations, L=100, v_max=5, observ_delay=0.1))


        # Couplings
        for i, generator in enumerate(self.generators):
            connect_segments(self, generator, self.generator_segments[i][0])
            for j in range(num_connecting_roads - 1):
                connect_segments(self, self.generator_segments[i][j], self.generator_segments[i][j + 1])
            connect_crossroads(self, self.generator_segments[i][-1], self.crossroads, i, input=True)

        for i, collector in enumerate(self.collectors):
            connect_crossroads(self, self.collector_segments[i][0], self.crossroads, i, input=False)
            for j in range(num_connecting_roads - 1):
                connect_segments(self, self.collector_segments[i][j], self.collector_segments[i][j + 1])
            connect_segments(self, self.collector_segments[i][-1], collector)



if __name__ == '__main__':
    # Short simulation
    model = NWayCrossroads("crossroads")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(1000)
    sim.setVerbose()
    sim.simulate()

    print("----------- Short simulation -----------")
    print(model.collectors)
    print("----------------------------------------")

    # Long simulation
    model = NWayCrossroads("crossroads")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(1000)
    sim.simulate()

    print("----------- Long simulation -----------")
    print(model.collectors)
    print("---------------------------------------")
