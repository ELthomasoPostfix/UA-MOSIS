from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
from pypdevs.simulator import Simulator

from components.generator import Generator
from components.collector import Collector
from components.roadsegment import RoadSegment
from components.gasstation import GasStation
from components.sidemarker import SideMarker
from components.fork import Fork

from other.road_stitcher import connect_pieces

class RoadStretch(CoupledDEVS):
    """Represents a segment of road connecting a Generator to Collector, with a fork and gas station in between.
    """

    def __init__(self, block_name: str, L: float = 10.0, v_max: float = 12.0,
                 IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                 limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None):
        """
        :param block_name: The name for this model. Must be unique inside a (parent) Coupled DEVS.
        """
        super(RoadStretch, self).__init__(block_name)

        num_gen_connect = 2
        num_col_connect = 2


        # Components
        # TODO: Placeholder values, make parameters as "realistic" as possible (find formula of reaction time w.r.t to speed)
        self.generator = self.addSubModel(Generator("gen", IAT_min=IAT_min, IAT_max=IAT_max, v_pref_mu=v_pref_mu,
                                                    v_pref_sigma=v_pref_sigma, destinations=["A"], limit=limit,
                                                    rng_seed=rng_seed))

        self.seg_gen = [self.addSubModel(RoadSegment(f"seg_gen_{i}", L=L, v_max=v_max, observ_delay=observ_delay)) for i in range(num_gen_connect)]

        self.fork = self.addSubModel(Fork("fork", L=L, v_max=v_max, observ_delay=observ_delay))

        self.upper_seg1 = self.addSubModel(RoadSegment("upper_seg1", L=L, v_max=v_max, observ_delay=observ_delay))
        self.upper_seg2 = self.addSubModel(RoadSegment("upper_seg2", L=L, v_max=v_max, observ_delay=observ_delay))
        self.upper_seg3 = self.addSubModel(RoadSegment("upper_seg3", L=L, v_max=v_max, observ_delay=observ_delay, priority=True))

        self.lower_seg1 = self.addSubModel(RoadSegment("lower_seg1", L=L, v_max=v_max, observ_delay=observ_delay, lane=1))
        self.lower_gas = self.addSubModel(GasStation("lower_gas", observ_delay=observ_delay))
        self.lower_seg2 = self.addSubModel(RoadSegment("lower_seg2", L=L, v_max=v_max, observ_delay=observ_delay, lane=1))

        self.merge_marker = self.addSubModel(SideMarker("merge_marker"))

        self.seg_col = [self.addSubModel(RoadSegment(f"seg_col_{i}", L=L, v_max=v_max, observ_delay=0.1)) for i in range(num_col_connect)]
        
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

        self.connectPorts(self.upper_seg3.Q_sack, self.merge_marker.mi)
        self.connectPorts(self.merge_marker.mo, self.lower_seg2.Q_rack)



def print_run_stats(model: RoadStretch):
    num_departures = model.generator.state.n
    num_arrivals = model.collector.state.n
    segments = [
        *model.seg_gen,
        model.fork, model.upper_seg1, model.upper_seg2, model.upper_seg3,
        model.lower_seg1, model.lower_seg2,
        *model.seg_col
    ]
    crashes = [(component.name, component.state.collisions) for component in segments]
    num_crashes = sum(collisions for (_, collisions) in crashes)

    print(f"Departures: {num_departures}")
    print(f"Arrivals: {num_arrivals}")
    print(f"Arrivals percentage: {num_arrivals / num_departures * 100}%")
    print(f"Total collisions: {2 * num_crashes}")

    assert num_arrivals + 2 * num_crashes == num_departures, "Diff amount of cars outputted than existed in the system"
    return num_crashes




def run_simulation(simulation_time: int, L: float = 10.0, v_max: float = 12.0,
            IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                 limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None):

    model = RoadStretch("crossroads", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max,
                           v_pref_mu=v_pref_mu, v_pref_sigma=v_pref_sigma, limit=limit,
                           observ_delay=observ_delay, rng_seed=rng_seed)
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(simulation_time)
    sim.setVerbose()
    sim.simulate()
    score = print_run_stats(model)

    return score


if __name__ == '__main__':
    # Short simulation
    run_simulation(5000, limit=100)

    # # Long simulation
    # model = RoadStretch("road_stretch")
    # sim = Simulator(model)
    # sim.setClassicDEVS()
    # sim.setTerminationTime(L0)
    # sim.simulate()
    #
    # print("----------- Long simulation -----------")
    # print(model.collector)
    # print("---------------------------------------")
