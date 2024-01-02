from itertools import chain
from typing import List
from pypdevs.DEVS import AtomicDEVS

from components.roadsegment import RoadSegment


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

