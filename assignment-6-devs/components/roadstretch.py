from pypdevs.DEVS import CoupledDEVS

from components.generator import Generator
from components.collector import Collector
from components.roadsegment import RoadSegment
from components.gasstation import GasStation
from components.sidemarker import SideMarker
from components.fork import Fork

from other.road_stitcher import connect_pieces, merge_segments


class RoadStretch(CoupledDEVS):
    """Represents a segment of road connecting a Generator to Collector, with a fork and gas station in between.
    """

    def __init__(self, block_name: str, 
                 generator_segment_count: int = 2, collector_segment_count: int = 2,
                 L_upper: float = 10.0, L_lower: float = 10.0, L_conn: float = 10.0,
                 v_max: float = 12.0, v_max_gas: float = 12.0,
                 IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                 limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None):
        """
        :param block_name: The name for this model. Must be unique inside a (parent) Coupled DEVS.
        """
        super(RoadStretch, self).__init__(block_name)

        # Components
        # TODO: Placeholder values, make parameters as "realistic" as possible (find formula of reaction time w.r.t to speed)
        self.generator = self.addSubModel(Generator("gen", IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                                                    v_pref_sigma=v_pref_sigma, destinations=["A"], limit=limit,
                                                    rng_seed=rng_seed))

        self.seg_gen = [self.addSubModel(RoadSegment(f"seg_gen_{i}", L=L_conn, v_max=v_max, observ_delay=observ_delay)) for i in range(generator_segment_count)]

        self.fork = self.addSubModel(Fork("fork", L=L_conn, v_max=v_max, observ_delay=observ_delay))

        self.upper_seg1 = self.addSubModel(RoadSegment("upper_seg1", L=L_upper, v_max=v_max, observ_delay=observ_delay))
        self.upper_seg2 = self.addSubModel(RoadSegment("upper_seg2", L=L_upper, v_max=v_max, observ_delay=observ_delay))
        self.upper_seg3 = self.addSubModel(RoadSegment("upper_seg3", L=L_upper, v_max=v_max, observ_delay=observ_delay, priority=True))

        self.lower_seg1 = self.addSubModel(RoadSegment("lower_seg1", L=L_lower, v_max=v_max_gas, observ_delay=observ_delay, lane=1))
        self.lower_gas = self.addSubModel(GasStation("lower_gas", observ_delay=observ_delay))
        self.lower_seg2 = self.addSubModel(RoadSegment("lower_seg2", L=L_lower, v_max=v_max_gas, observ_delay=observ_delay, lane=1))

        self.merge_marker = self.addSubModel(SideMarker("merge_marker"))

        self.seg_col = [self.addSubModel(RoadSegment(f"seg_col_{i}", L=L_conn, v_max=v_max, observ_delay=0.1)) for i in range(collector_segment_count)]
        
        self.collector = self.addSubModel(Collector("col"))

        # Couplings
        road_layout = [
            self.generator,
            *self.seg_gen,
            (self.fork, (
                [self.upper_seg1, self.upper_seg2, self.upper_seg3],
                [self.lower_seg1, self.lower_gas, self.lower_seg2],
            )),
            *self.seg_col,
            self.collector
        ]

        connect_pieces(self, road_layout)
        merge_segments(self, self.upper_seg3, self.lower_seg2, self.seg_col[0], self.merge_marker)