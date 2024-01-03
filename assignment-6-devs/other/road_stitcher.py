from itertools import chain
from typing import List
from pypdevs.DEVS import AtomicDEVS, CoupledDEVS

from components.roadsegment import RoadSegment
from components.sidemarker import SideMarker


def get_ends(segment):
    if isinstance(segment, tuple):
        return list(chain.from_iterable([get_ends(seg) for seg in segment[1]]))
    elif isinstance(segment, list):
        return [*get_ends(segment[-1])]
    else:
        return [segment]


def connect_pieces(component: CoupledDEVS, segments):
    for i in range(len(segments) - 1):
        connect_piece(component, segments[i], segments[i + 1])
    return segments[0]


def connect_piece(component: CoupledDEVS, seg1, seg2):
    if isinstance(seg2, tuple):
        connect_segments(component, seg1, seg2[0])
        for i, seg_road in enumerate(seg2[1]):
            seg_start = connect_pieces(component, seg_road)
            connect_segments(component, seg2[0], seg_start, bool(i))
    else:
        for end in get_ends(seg1):
            connect_segments(component, end, seg2)


def connect_segments(component: CoupledDEVS, seg1, seg2, is_forked=False):
    component.connectPorts(seg1.car_out if not is_forked else seg1.car_out2, seg2.car_in)
    if isinstance(seg2, RoadSegment):
        component.connectPorts(seg1.Q_send, seg2.Q_recv)
        component.connectPorts(seg2.Q_sack, seg1.Q_rack)


def connect_crossroads(component: CoupledDEVS, seg, cr, i, input=False):
    if input:
        component.connectPorts(seg.car_out, cr.car_in_x[i])
        component.connectPorts(seg.Q_send, cr.Q_recv_x[i])
        component.connectPorts(cr.Q_sack_x[i], seg.Q_rack)
    else:
        next_seg = (i + 1) % len(cr.destinations)
        component.connectPorts(cr.car_out_x[next_seg], seg.car_in)
        component.connectPorts(cr.Q_send_x[next_seg], seg.Q_recv)
        component.connectPorts(seg.Q_sack, cr.Q_rack_x[next_seg])



CONNECTING_PORTS = [("car_out", "car_in"), ("Q_send", "Q_recv"), ("Q_rack", "Q_sack")]


def has_port_connection(seg1: RoadSegment, seg2: RoadSegment, port1: str, port2: str) -> bool:
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


def segments_connected(seg1: RoadSegment, seg2: RoadSegment) -> bool:
    """
    :param seg1: The first RoadSegment.
    :param seg2: The second RoadSegment.
    :return: True if the two RoadSegments are fully connected, False otherwise.
    """
    return all(has_port_connection(seg1, seg2, port1, port2) for port1, port2 in CONNECTING_PORTS)


def merge_segments(component: CoupledDEVS,
                priority_seg: RoadSegment,
                regular_seg: RoadSegment,
                output_seg: RoadSegment,
                merge_marker: SideMarker):
    """Connect two RoadSegments to a SideMarker, representing a merge.

    :param component: The CoupledDEVS to connect the components in.
    :param priority_seg: The RoadSegment that has priority.
    :param regular_seg: The RoadSegment that does not have priority.
    :param output_seg: The RoadSegment that is the output of the merge.
    :param merge_marker: The SideMarker to connect to.
    """

    try:
        priority_seg.seg.priority = True
    except AttributeError:
        pass

    # Check if ports are already connected

    # if not segments_connected(priority_seg, output_seg):
    #     connect_segments(component, priority_seg, output_seg)
    # if not segments_connected(regular_seg, output_seg):
    #     connect_segments(component, regular_seg, output_seg)




    # Regular segment
    # 'crossroads.cr.cr_seg_3.Q_send'
    # crossroads.cr.cr_seg_3.Q_send -> crossroads.cr.Q_send_0
    # crossroads.cr.cr_seg_3.Q_send -> crossroads.cr.cr_seg_0.Q_recv

    # Priority segment
    # 'crossroads.cr.Q_recv_0'
    # crossroads.gen_0_seg_2.Q_send -> crossroads.cr.Q_recv_0
    # +++ crossroads.gen_0_seg_3.Q_send -> crossroads.cr.Q_recv_0
    #

    component.connectPorts(regular_seg.Q_send, priority_seg.Q_recv)     # regular  -> priority
    component.connectPorts(priority_seg.Q_sack, merge_marker.mi)        # priority -> marker
    component.connectPorts(merge_marker.mo, regular_seg.Q_rack)         # marker   -> regular
