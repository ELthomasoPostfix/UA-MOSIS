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


def connect_pieces(self, segments):
    for i in range(len(segments) - 1):
        connect_piece(self, segments[i], segments[i + 1])
    return segments[0]


def connect_piece(self, seg1, seg2):
    if isinstance(seg2, tuple):
        connect_segments(self, seg1, seg2[0])
        for i, seg_road in enumerate(seg2[1]):
            seg_start = connect_pieces(self, seg_road)
            connect_segments(self, seg2[0], seg_start, bool(i))
    else:
        for end in get_ends(seg1):
            connect_segments(self, end, seg2)


def connect_segments(self, seg1, seg2, is_forked=False):
    self.connectPorts(seg1.car_out if not is_forked else seg1.car_out2, seg2.car_in)
    if isinstance(seg2, RoadSegment):
        self.connectPorts(seg1.Q_send, seg2.Q_recv)
        self.connectPorts(seg2.Q_sack, seg1.Q_rack)


def connect_crossroads(self, seg, cr, i, input=False):
    if input:
        self.connectPorts(seg.car_out, cr.car_in_x[i])
        self.connectPorts(seg.Q_send, cr.Q_recv_x[i])
        self.connectPorts(cr.Q_sack_x[i], seg.Q_rack)
    else:
        self.connectPorts(cr.car_out_x[i], seg.car_in)
        self.connectPorts(cr.Q_send_x[i], seg.Q_recv)
        self.connectPorts(seg.Q_sack, cr.Q_rack_x[i])

