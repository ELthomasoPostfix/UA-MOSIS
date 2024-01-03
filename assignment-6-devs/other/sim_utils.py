import json

from pypdevs.simulator import Simulator

from components.roadstretch import RoadStretch
from components.n_way_crossroads import NWayCrossroads
from components.crossroads import CrossRoads, ROWCrossRoads, RoundaboutCrossRoads

from itertools import chain


def print_rs_run_stats(model: RoadStretch, stats_header: str, output_file_path: str = ""):
    """Print the statistics that can be collected from the
    given *model* AFTER the simulation has concluded.
    
    :param model: The model to collect stats from
    :param stats_header: A text message to display right above the printed stats
    """
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
    num_crashed_cars = 2 * num_crashes


    print(stats_header)
    print(f"Departures:          {num_departures}")
    print(f"Total collisions:    {num_crashed_cars}")
    print(f"Arrivals:            {num_arrivals}")
    print(f"Arrivals percentage: {num_arrivals / num_departures * 100}%")
    print(f"Last generator out:  {model.generator.state.latest_departure_time}")
    print(f"Last collector inp:  {model.collector.state.latest_arrival_time}")
    print(f"N no_gas:            {model.collector.state.n_no_gas}")

    if output_file_path is not None and output_file_path != "":
        with open(output_file_path, "w") as of:
            json_str: str = json.dumps({
                "departures": num_departures,
                "collisions": num_crashes,
                "arrivals": num_arrivals,
                "generators": [
                    {
                        "name": model.generator.name,
                        "n": model.generator.state.n,
                        "latest_departure_time": model.generator.state.latest_departure_time
                    }
                ],
                "collectors": [
                    {
                        "name": model.collector.name,
                        "n": model.collector.state.n,
                        "n_no_gas": model.collector.state.n_no_gas,
                        "latest_arrival_time": model.collector.state.latest_arrival_time,
                        "travel_stats": model.collector.state.car_travel_stats,
                    }
                ]
            }, indent=4)
            of.write(json_str)
            print(f"Wrote output to:     {output_file_path}")

    assert (num_arrivals + num_crashed_cars) == num_departures, "Diff amount of cars outputted than existed in the system"
    return num_crashed_cars

def print_cw_run_stats(model: NWayCrossroads, stats_header: str, output_file_path: str = ""):
    """Print the statistics that can be collected from the
    given *model* AFTER the simulation has concluded.

    :param model: The model to collect stats from
    :param stats_header: A text message to display right above the printed stats
    """
    num_departures = [generator.state.n for generator in model.generators]
    num_arrivals = [collector.state.n for collector in model.collectors]
    segments = [
        *chain(*model.generator_segments),
        *model.crossroads.segments,
        *chain(*model.collector_segments)
    ]
    crashes = [(component.name, component.state.collisions) for component in segments]
    num_crashes = sum(collisions for (_, collisions) in crashes)
    num_crashed_cars = 2 * num_crashes

    print(stats_header)
    print(f"Departures:          {sum(num_departures)}")
    print(f"Total collisions:    {num_crashed_cars}")
    print(f"Arrivals:            {sum(num_arrivals)}")
    print(f"Arrivals percentage: {sum(num_arrivals) / sum(num_departures) * 100}%")
    print(f"N no_gas:            {sum([collector.state.n_no_gas for collector in model.collectors])}")

    if output_file_path is not None and output_file_path != "":
        with open(output_file_path, "w") as of:
            json_str: str = json.dumps({
                "departures": sum(num_departures),
                "collisions": num_crashes,
                "arrivals": sum(num_arrivals),
                "generators": [
                    {
                        "name": generator.name,
                        "n": generator.state.n,
                        "latest_departure_time": generator.state.latest_departure_time
                    }
                    for generator in model.generators
                ],
                "collectors": [
                    {
                        "name": collector.name,
                        "n": collector.state.n,
                        "n_no_gas": collector.state.n_no_gas,
                        "latest_arrival_time": collector.state.latest_arrival_time,
                        "travel_stats": collector.state.car_travel_stats,
                    }
                    for collector in model.collectors
                ]
            }, indent=4)
            of.write(json_str)
            print(f"Wrote output to:     {output_file_path}")

    assert (sum(num_arrivals) + num_crashed_cars) == sum(num_departures), "Diff amount of cars outputted than existed in the system"
    return num_crashes


def run_rs_simulation(simulation_time: int, L: float = 10.0, v_max: float = 12.0,
                   IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                   limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None,
                   verbose: bool = False, output_file_path: str = "", draw_dot = False):

    model = RoadStretch("roadstretch", L=L, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max,
                           v_pref_mu=v_pref_mu, v_pref_sigma=v_pref_sigma, limit=limit,
                           observ_delay=observ_delay, rng_seed=rng_seed)
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(simulation_time)
    if verbose:
        sim.setVerbose()

    if draw_dot:
        sim.setDrawModel(True, 'model.dot', False)

    sim.simulate()
    score = print_rs_run_stats(model, f"=== {simulation_time} (termination time) ===", output_file_path)

    return score


# def run_simulation(simulation_time: int, L: float = 10.0, L_cr: float = 5, v_max: float = 12.0,
#             IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
#                  limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None):

def run_cw_simulation(simulation_time: int, crossroad_type: CrossRoads = CrossRoads,
                    branch_count: int = 4, branch_segment_amount: int = 3,
                      L: float = 10.0, L_cr: float = 5, v_max: float = 12.0,
            IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                 limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None,
                 verbose: bool = False, output_file_path: str = "", draw_dot = False):
    model = NWayCrossroads(crossroad_type.__name__,crossroad_type=crossroad_type, branch_count=branch_count, branch_segment_amount=branch_segment_amount, L=L,
                           L_cr=L_cr, v_max=v_max, IAT_min=IAT_min, IAT_max=IAT_max,
                           v_pref_mu=v_pref_mu, v_pref_sigma=v_pref_sigma, limit=limit, observ_delay=observ_delay,
                           rng_seed=rng_seed)
    sim = Simulator(model)
    sim.setClassicDEVS()
    sim.setTerminationTime(simulation_time)
    if verbose:
        sim.setVerbose()

    if draw_dot:
        sim.setDrawModel(True, 'model.dot', False)

    sim.simulate()
    score = print_cw_run_stats(model, f"=== {simulation_time} (termination time) ===", output_file_path)

    return score
