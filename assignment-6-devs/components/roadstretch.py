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

    def __init__(self, block_name: str):
        """
        :param block_name: The name for this model. Must be unique inside a (parent) Coupled DEVS.
        """
        super(RoadStretch, self).__init__(block_name)

        num_gen_connect = 2
        num_col_connect = 2


        # Components
        # TODO: Placeholder values, make parameters as "realistic" as possible (find formula of reaction time w.r.t to speed)
        self.generator = self.addSubModel(Generator("gen", IAT_min=0.5, IAT_max=1.5, v_pref_mu=5,
                                                    v_pref_sigma=1, destinations=["A"], limit=100))

        self.seg_gen = [self.addSubModel(RoadSegment(f"seg_gen_{i}", L=100, v_max=5, observ_delay=0.1)) for i in range(num_gen_connect)]

        self.fork = self.addSubModel(Fork("fork", L=100, v_max=5, observ_delay=0.1))

        self.upper_seg1 = self.addSubModel(RoadSegment("upper_seg1", L=100, v_max=5, observ_delay=0.1))
        self.upper_seg2 = self.addSubModel(RoadSegment("upper_seg2", L=100, v_max=5, observ_delay=0.1))
        self.upper_seg3 = self.addSubModel(RoadSegment("upper_seg3", L=100, v_max=5, observ_delay=0.1, priority=True))

        self.lower_seg1 = self.addSubModel(RoadSegment("lower_seg1", L=100, v_max=5, observ_delay=0.1, lane=1))
        self.lower_gas = self.addSubModel(GasStation("lower_gas", observ_delay=0.1))
        self.lower_seg2 = self.addSubModel(RoadSegment("lower_seg2", L=100, v_max=5, observ_delay=0.1, lane=1))

        self.merge_marker = self.addSubModel(SideMarker("merge_marker"))

        self.seg_col = [self.addSubModel(RoadSegment(f"seg_col_{i}", L=100, v_max=5, observ_delay=0.1)) for i in range(num_col_connect)]
        
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


if __name__ == '__main__':
    # Short simulation
    model = RoadStretch("road_stretch")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(100)
    sim.setVerbose()
    sim.simulate()

    print("----------- Short simulation -----------")
    print(model.collector)
    print("----------------------------------------")

    # Long simulation
    model = RoadStretch("road_stretch")
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(1000)
    sim.simulate()

    print("----------- Long simulation -----------")
    print(model.collector)
    print("---------------------------------------")
