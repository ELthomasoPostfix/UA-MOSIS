from components.messages import Car, QueryAck
from components.roadsegment import Priority


def clamp_speed(car: Car, v_target: float):
    """Return the new speed that the *car* would like to attain if possible.

    This method implements the acceleration or deceleration of the *car*'s
    speed towards its v_pref.

    :return: The desired new speed
    """
    # Accel/Decel to v_target according to dv_pos_max/dv_neg_max
    v: float
    if car.v < v_target:
        speed_max_accel: float = car.v + car.dv_pos_max
        v = min(speed_max_accel, v_target)
    elif car.v > v_target:
        speed_max_decel: float = car.v - car.dv_neg_max
        v = max(speed_max_decel, v_target)
    else:
        v = v_target
    return self._clamp(v, 0.0, self.v_max)




current_car: Car = Car(
    ID=1, v=15.0, v_pref=15.0, dv_pos_max=10.0, dv_neg_max=10.0, departure_time=0.0,
    distance_traveled=0.0,  no_gas=False,
    destination="A"
)

remaining_x = 10.0

time_until_next_seg_clear = 0.0

query_ack: QueryAck = QueryAck(1, time_until_next_seg_clear, sideways=True)
t_no_coll = query_ack.t_until_dep

curr_seg_priority = False



if not query_ack.sideways:
    v_new = clamp_speed(current_car, current_car.v_pref)
    t_exit = remaining_x / v_new
    # Car will arrive at next RoadSegment while it is still occupied by another Car
    # Collision will occur, slow down to the minimum speed such that collision is avoided
    if t_no_coll > t_exit:
        v_new = remaining_x / t_no_coll
        priority_int = Priority.P1
    # No collision, keep v_new as is
    else:
        pass
else:
    if not curr_seg_priority:
        # Decelerate to zero as fast as possible
        # i.e. the target speed is 0.0
        v_new = 0.0
        priority_int = Priority.P2
    else:
        v_new = current_car.v_pref
v_new = clamp_speed(current_car, v_new)


print(v_new)





























