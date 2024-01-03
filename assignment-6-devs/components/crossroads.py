from pypdevs.DEVS import CoupledDEVS
from pypdevs.simulator import Simulator

from components.roadsegment import RoadSegment
from components.sidemarker import SideMarker

from other.road_stitcher import connect_segments


class CrossRoadSegment(RoadSegment):
    """Acts as if it were a part of a crossroads. I.e., this is a location where two roads merge and split at the same time.
    Combining multiple of these segments together results in a CrossRoad.

    Given that this block inherits from RoadSegment, all aspects discussed there are also applicable.
    """
    def __init__(self, block_name: str, L: float, v_max: float,
                 observ_delay: float = 0.1, priority: bool = False, lane: int = 0,
                 destinations: list = None):
        """
        :param block_name: The name for this model. Must be unique inside a Coupled DEVS.
        :param L: The length of the RoadSegment. Given that the average Car is about 5 meters in length, a good estimate value for L would therefore be 5 meters.
        :param v_max: The maximal allowed velocity on this RoadSegment.
        :param observ_delay: The time it takes to reply to a Query that was inputted. This value mimics the reaction time of the driver. We can increase the observ_delay to accomodate for bad weather situations (e.g., a lot of fog and/or rain). Defaults to 0.1.
        :param priority: Whether or not this RoadSegment should have priority on a merge with other road segments. Defaults to False.
        :param lane: Indicator of the lane this Roadsegment is currently part of. Defaults to 0.
        :param destinations: A list of destinations reachable when a car exits the crossroads at this location. This list will be initialized upon creation of the road map and should not be changed afterwards. It is used to make sure Cars exit the crossroads at the right time.
        """
        super(CrossRoadSegment, self).__init__(block_name=block_name, L=L, v_max=v_max,
                         observ_delay=observ_delay, priority=priority, lane=lane)

        self.destinations: list = destinations if destinations is not None else list()
        """A list of destinations reachable when a car exits the crossroads at this location. Is immutable, so its should NOT be part of the model state member."""

        # Ports
        self.car_in_cr = self.addInPort("car_in_cr")
        """Cars can enter on this segment as if it were the normal car_in port. However, this port is only used for Cars that were already on the crossroads. Potentially, this information may be stored in the cars_present list, but is merely used for a clean separation and to potentially allow other behaviour in the future."""
        self.car_out_cr = self.addOutPort("car_out_cr")
        """Outputs the Cars that must stay on the crossroads. In essence, these are all the Cars that have a destination not in this CrossRoadSegment's destinations field."""

    def extTransition(self, inputs):
        """May edit state."""

        # Give car_in_cr precedence over the RoadSegment input ports.
        if self.car_in_cr in inputs:
            # The super extTransition is not called, so be sure to update the timers appropriately
            self._update_multiple_timers(self.elapsed)
            # Actually handle entering the car
            self.car_enter(inputs[self.car_in_cr])

            # After entering a car into the CrossRoads through the car_in_cr port,
            # we HAVE TO return the state and NOT run the super extTransition.
            #   1) Semantically, the extTransition function of an AtomicDEVS should
            #      be deterministic, and all needed logic for entering the car through
            #      the car_in_cr port is handled using the car_enter method. Running
            #      the super extTransition is then redundant, because the car_in_cr
            #      event was handled during this call.
            #   2) Functionally, the car_enter method called above sets the t_until_send_query
            #      timer to 0.0s. Calling the super extTransition as well will update
            #      the t_until_send_query timer again be decreasing it by self.elapsed.
            #      This will result in a negative timeAdvance() output.
            return self.state

        return super(CrossRoadSegment, self).extTransition(inputs)


    def outputFnc(self):
        """May NOT edit state."""

        output: dict = super(CrossRoadSegment, self).outputFnc()
        if self.car_out in output:
            car = output[self.car_out]
            if car.destination not in self.destinations:
                output[self.car_out_cr] = car
                del output[self.car_out]
        return output


class CrossRoads(CoupledDEVS):
    """Represents a free-for-all n-way crossroads.
    
    The internal representation for a 4-way implementation is as shown in the assignment.
    For the sake of readability, the outer ports are here encoded using North (N), East (E), South (S), West (W);
    instead of using indexes. This same encoding is used to distinguish between the individual CrossRoadSegments in the image.
    """
    def __init__(self, block_name: str, destinations: list, L: float,
                 v_max: float, observ_delay: float):
        """
        :param block_name: The name for this model. Must be unique inside a (parent) Coupled DEVS.
        :param destinations: A list of lists of destinations for the CrossRoads. The amount of sub-lists indicates how many branches the CrossRoads has. Each sub-list is given to the CrossRoadSegments in order.
        :param L: The length of the individual CrossRoadSegments.
        :param v_max: The maximal allowed velocity on the CrossRoads.
        :param observ_delay: The observ_delay for the CrossRoadSegments.
        """
        super(CrossRoads, self).__init__(block_name)

        # Immutable members -- should NOT be part of the model state member
        self.destinations: list = destinations
        self.L: float = L
        self.v_max: float = v_max
        self.observ_delay: float = observ_delay

        num_branches = len(destinations)

        # Components
        self.segments = [
            self.addSubModel(CrossRoadSegment(f"{block_name}_seg_{i}", L, v_max, observ_delay, lane=i, destinations=destinations[i]))
            for i in range(num_branches)
        ]

        # Ports
        self.car_in_x = [self.addInPort(f"car_in_{i}") for i in range(num_branches)]
        """Cars can enter the crossroads through this port. The * indicates an integer representing which branch of the crossroads this port will be linked to. For each of the branches, a car_in_* port exists, which links to the same-index CrossRoadSegment."""
        self.Q_recv_x = [self.addInPort(f"Q_recv_{i}") for i in range(num_branches)]
        """Allows the crossroads to receive Query events on the associated branch. The * indicates an integer representing which branch of the crossroads this port will be linked to. For each of the branches, a Q_recv_* port exists, which links to the same-index CrossRoadSegment."""
        self.Q_rack_x = [self.addInPort(f"Q_rack_{i}") for i in range(num_branches)]
        """Allows the crossroads to receive QueryAck events. The * indicates an integer representing which branch of the crossroads this port will be linked to. For each of the branches, a Q_rack_* port exists, which links to the next-index CrossRoadSegment."""
        self.car_out_x = [self.addOutPort(f"car_out_{i}") for i in range(num_branches)]
        """Outputs the Cars on this branch of the crossroads. The * indicates an integer representing which branch of the crossroads this port will be linked to. For each of the branches, a car_out_* port exists, which comes from the next-index CrossRoadSegment."""
        self.Q_send_x = [self.addOutPort(f"Q_send_{i}") for i in range(num_branches)]
        """Outputs the Query events on this branch of the crossroads. The * indicates an integer representing which branch of the crossroads this port will be linked to. For each of the branches, a Q_send_* port exists, which comes from the next-index CrossRoadSegment. The Q_send_* port also links to the Q_recv_* port of the next CrossRoadSegment, making sure Cars can drive without issues over the crossroads."""
        self.Q_sack_x = [self.addOutPort(f"Q_sack_{i}") for i in range(num_branches)]
        """Outputs the QueryAck events on this branch of the crossroads. The * indicates an integer representing which branch of the crossroads this port will be linked to. For each of the branches, a Q_sack_* port exists, which comes from the same-index CrossRoadSegment. The Q_sack_* port also links to the Q_rack_* port of the previous CrossRoadSegment, making sure Cars can drive without issues over the crossroads."""

        # Couplings
        for i in range(num_branches):
            next_seg = (i + 1) % num_branches
            # External connections
            self.connectPorts(self.car_in_x[i], self.segments[i].car_in)
            self.connectPorts(self.segments[i].Q_sack, self.Q_sack_x[i])
            self.connectPorts(self.Q_recv_x[i], self.segments[i].Q_recv)

            self.connectPorts(self.segments[i].car_out, self.car_out_x[next_seg])
            self.connectPorts(self.Q_rack_x[next_seg], self.segments[i].Q_rack)
            self.connectPorts(self.segments[i].Q_send, self.Q_send_x[next_seg])

            # Internal connections
            self.connectPorts(self.segments[i].car_out_cr, self.segments[next_seg].car_in_cr)
            self.connectPorts(self.segments[i].Q_send, self.segments[next_seg].Q_recv)
            self.connectPorts(self.segments[next_seg].Q_sack, self.segments[i].Q_rack)


class ROWCrossRoads(CrossRoads):

    def __init__(self, block_name: str, destinations: list, L: float,
                 v_max: float, observ_delay: float):
        super(ROWCrossRoads, self).__init__(block_name, destinations, L, v_max, observ_delay)

        self.merge_markers = [self.addSubModel(SideMarker(f"merge_marker_{i}")) for i in range(len(destinations))]

        for i in range(len(destinations)):
            prev_seg = i - 1 % len(destinations)
            self.connectPorts(self.Q_rack_x[i], self.merge_markers[i].mi)
            self.connectPorts(self.merge_markers[i].mo, self.segments[prev_seg].Q_rack)
            self.connectPorts(self.segments[prev_seg].Q_send, self.Q_send_x[i])


class RoundaboutCrossRoads(CrossRoads):

    def __init__(self, block_name: str, destinations: list, L: float,
                 v_max: float, observ_delay: float):
        super(RoundaboutCrossRoads, self).__init__(block_name, destinations, L, v_max, observ_delay)

        self.merge_markers = [self.addSubModel(SideMarker(f"merge_marker_{i}")) for i in range(len(destinations))]

        for i in range(len(destinations)):
            prev_seg = i - 1 % len(destinations)
            self.connectPorts(self.segments[prev_seg].Q_sack, self.merge_markers[i].mi)
            self.connectPorts(self.merge_markers[i].mo, self.Q_sack_x[i])
            self.connectPorts(self.Q_recv_x[i], self.segments[prev_seg].Q_recv)

            self.segments[i].priority = True





if __name__ == '__main__':
    model = CrossRoads("crossroads", destinations=[["A"], ["B"], ["C"], ["D"]], L=100, v_max=5, observ_delay=0.1)
    sim = Simulator(model)
    sim.setDrawModel(True, "model.dot", False)
    sim.simulate()
