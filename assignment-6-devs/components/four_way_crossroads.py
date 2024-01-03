from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.simulator import Simulator

from components.generator import Generator
from components.collector import Collector
from components.roadsegment import RoadSegment
from components.crossroads import CrossRoads


from other.road_stitcher import connect_segments, connect_crossroads


from itertools import chain
from scipy.optimize import minimize

import logging
# logging.basicConfig(level=logging.DEBUG)

class NWayCrossroads(CoupledDEVS):
    """Represents a segment of road connecting a Generator to Collector, with a fork and gas station in between.
    """

    def __init__(self, block_name: str, L: float = 10.0, L_cr: float = 5, v_max: float = 12.0,
            IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                 limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None):
        # TODO uncomment for randomness, leave commented for set SEED
        """
        :param block_name: The name for this model. Must be unique inside a (parent) Coupled DEVS.
        """
        super(NWayCrossroads, self).__init__(block_name)

        num_connections = 4
        num_connecting_roads = 3

        # Components
        self.collectors = [self.addSubModel(Collector(f"col_{i}")) for i in range(num_connections)]
        destinations = [collector.name for collector in self.collectors]
        self.generators = [self.addSubModel(Generator(f"zgen_{i}",
                                                      IAT_min=IAT_min,
                                                      IAT_max=IAT_max,
                                                      v_pref_mu=v_pref_mu,
                                                      v_pref_sigma=v_pref_sigma,
                                                      destinations=destinations,
                                                      limit=limit,
                                                      rng_seed=rng_seed))
                           for i in range(num_connections)]


        self.collector_segments = [
            [
                self.addSubModel(RoadSegment(f"col_{i}_seg_{j}", L=L, v_max=v_max, observ_delay=observ_delay))
                for j in range(num_connecting_roads)
            ]
            for i in range(num_connections)
        ]
        self.generator_segments = [
            [
                self.addSubModel(RoadSegment(f"gen_{i}_seg_{j}", L=L,
                                             v_max=v_max, observ_delay=observ_delay))
                for j in range(num_connecting_roads)
            ]
            for i in range(num_connections)
        ]

        crossroads_destinations = [ [f"col_{i}"] for i in range(num_connections)]

        self.crossroads = self.addSubModel(CrossRoads("cr", destinations=crossroads_destinations,
                                                      L=L_cr, v_max=v_max, observ_delay=observ_delay))


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
