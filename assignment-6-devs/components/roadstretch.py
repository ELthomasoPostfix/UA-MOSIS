from pypdevs.DEVS import CoupledDEVS

from components.generator import Generator
from components.collector import Collector
from components.roadsegment import RoadSegment
from components.gasstation import GasStation
from components.sidemarker import SideMarker
from components.fork import Fork

from other.road_stitcher import connect_pieces




connecting_ports = [("car_out", "car_in"), ("Q_send", "Q_recv"), ("Q_rack", "Q_sack")]


def is_connected(seg1: RoadSegment, seg2: RoadSegment, port1: str, port2: str) -> bool:
    """
    Check if *port1* is a name in the ports of *seg1* AND *port2* is a name in the ports of *seg*2.

    :param seg1: The first RoadSegment.
    :param seg2: The second RoadSegment.
    :param port1: The name of the port on the first RoadSegment.
    :param port2: The name of the port on the second RoadSegment.
    :return: True if the two ports are connected, False otherwise.
    """
    port1 = next((p for p in seg1.ports if p.name == port1), None)
    port2 = next((p for p in seg2.ports if p.name == port2), None)

    if port1 and port2:
        return port1 in port2.inline or port2 in port1.inline
    return False

def road_segments_connected(seg1: RoadSegment, seg2: RoadSegment) -> bool:
    """
    :param seg1: The first RoadSegment.
    :param seg2: The second RoadSegment.
    :return: True if the two RoadSegments are fully connected, False otherwise.
    """
    return all(is_connected(seg1, seg2, port1, port2) for port1, port2 in connecting_ports)


def merge_roads(component: CoupledDEVS,
                priority_seg: RoadSegment, regular_seg: RoadSegment, output_seg: RoadSegment,
                merge_marker: SideMarker):
    """Connect two RoadSegments to a SideMarker, representing a merge.

    :param component: The CoupledDEVS to connect the components in.
    :param priority_seg: The RoadSegment that has priority.
    :param regular_seg: The RoadSegment that does not have priority.
    :param output_seg: The RoadSegment that is the output of the merge.
    :param merge_marker: The SideMarker to connect to.
    """
    priority_seg.priority = True

    # Check if ports are already connected

    if not road_segments_connected(priority_seg, output_seg):
        connect_segments(priority_seg, output_seg)
        connect_segments(regular_seg, output_seg)

    component.connectPorts(regular_seg.Q_send, priority_seg.Q_recv)     # regular  -> priority
    component.connectPorts(priority_seg.Q_sack, merge_marker.mi)        # priority -> marker
    component.connectPorts(merge_marker.mo, regular_seg.Q_rack)         # marker   -> regular


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
        merge_roads(self, self.upper_seg3, self.lower_seg2, self.seg_col[0], self.merge_marker)