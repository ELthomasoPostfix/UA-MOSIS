import json

from pypdevs.simulator import Simulator

from components.roadstretch import RoadStretch
from components.n_way_crossroads import NWayCrossroads
from components.crossroads import CrossRoads, ROWCrossRoads, RoundaboutCrossRoads

from matplotlib import pyplot as plt
import seaborn as sns
from itertools import chain


def collect_rs_run_stats(model: RoadStretch):
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

    # assert (num_arrivals + num_crashed_cars) == num_departures, "Diff amount of cars outputted than existed in the system"

    return {
        "departures": num_departures,
        "collisions": num_crashes,
        "collision_places": crashes,
        "crashed_cars": 2 * num_crashes,
        "arrivals": num_arrivals,
        "crash_rate": 2 * num_crashes / num_departures,
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
                "avg_refuel_time": model.collector.state.total_refuel_time / model.collector.state.n_times_refueled if model.collector.state.n_times_refueled else 0.0
            }
        ]
    }

def print_rs_run_stats(stats: dict, stats_header: str):
    """Print the statistics that can be collected from the model AFTER the simulation has concluded.
    :param stats: The stats to print
    :param stats_header: A text message to display right above the printed stats
    """

    print(stats_header)
    print(f"Departures:          {stats['departures']}")
    print(f"Total collisions:    {stats['crashed_cars']}")
    print(f"Arrivals:            {stats['arrivals']}")
    print(f"Arrivals percentage: {stats['arrivals'] / stats['departures'] * 100}%")
    print(f"Last generator out:  {stats['generators'][0]['latest_departure_time']}")
    print(f"Last collector inp:  {stats['collectors'][0]['latest_arrival_time']}")
    print(f"N no_gas:            {stats['collectors'][0]['n_no_gas']}")


def collect_cw_run_stats(model: NWayCrossroads):
    num_departures = [generator.state.n for generator in model.generators]
    num_arrivals = [collector.state.n for collector in model.collectors]
    segments = [
        *chain(*model.generator_segments),
        *model.crossroads.segments,
        *chain(*model.collector_segments)
    ]
    crashes = [(component.name, component.state.collisions) for component in segments]
    num_crashes = sum(collisions for (_, collisions) in crashes)

    assert sum(num_arrivals) + 2 * num_crashes == sum(num_departures), "Diff amount of cars outputted than existed in the system"

    return {
        "departures": sum(num_departures),
        "collisions": num_crashes,
        "collision_places": crashes,
        "crashed_cars": 2 * num_crashes,
        "arrivals": sum(num_arrivals),
        "crash_rate": 2 * num_crashes / sum(num_departures),
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
    }


def save_run_stats(stats: dict, output_file_path: str):
    """Save the statistics collected from the model AFTER the simulation has concluded.
    :param stats: The stats to save
    :param output_file_path: The path to save the stats to
    """
    with open(output_file_path, "w") as of:
        json_str: str = json.dumps(stats, indent=4)
        of.write(json_str)
        print(f"Wrote output to:     {output_file_path}")

def print_cw_run_stats(stats: dict, stats_header: str):
    """Print the statistics collected from the model AFTER the simulation has concluded.
    :param stats: The stats to print
    :param model: The model to collect stats from
    :param stats_header: A text message to display right above the printed stats
    """

    print(stats_header)
    print(f"Departures:          {stats['departures']}")
    print(f"Total collisions:    {stats['crashed_cars']}")
    print(f"Arrivals:            {stats['arrivals']}")
    print(f"Arrivals percentage: {stats['arrivals'] / stats['departures'] * 100}%")
    print(f"N no_gas:            {sum(collector['n_no_gas'] for collector in stats['collectors'])}")


def run_rs_simulation(simulation_time: int,
                      generator_segment_count: int = 2, collector_segment_count: int = 2,
                      L_upper: float = 10.0, L_lower: float = 10.0, L_conn: float = 10.0,
                      v_max: float = 12.0, v_max_gas: float = 12.0,
                      IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                      limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None,
                      verbose: bool = False, output_file_path: str = "", draw_dot=False, print_stats=True):
    model = RoadStretch("roadstretch", generator_segment_count=generator_segment_count,
                        collector_segment_count=collector_segment_count,
                        L_upper=L_upper, L_lower=L_lower, L_conn=L_conn,
                        v_max=v_max, v_max_gas=v_max_gas,
                        IAT_min=IAT_min, IAT_max=IAT_max,
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
    results = collect_rs_run_stats(model)

    if print_stats:
        print_rs_run_stats(results, f"=== {simulation_time} (termination time) ===")
    if output_file_path is not None and output_file_path != "":
        save_run_stats(results, output_file_path)

    return results


# def run_simulation(simulation_time: int, L: float = 10.0, L_cr: float = 5, v_max: float = 12.0,
#             IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
#                  limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None):

def run_cw_simulation(simulation_time: int, crossroad_type: CrossRoads = CrossRoads,
                      branch_count: int = 4, branch_segment_amount: int = 3,
                      L: float = 10.0, L_cr: float = 5, v_max: float = 12.0,
                      IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
                      limit: int = 10, observ_delay: float = 0.1, rng_seed: int | None = None,
                      verbose: bool = False, output_file_path: str = "", draw_dot=False, print_stats=True):
    model = NWayCrossroads(crossroad_type.__name__, crossroad_type=crossroad_type, branch_count=branch_count,
                           branch_segment_amount=branch_segment_amount, L=L,
                           L_cr=L_cr, v_max=v_max,
                           IAT_min=IAT_min, IAT_max=IAT_max,
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

    results = collect_cw_run_stats(model)
    if print_stats:
        print_cw_run_stats(results, f"=== {simulation_time} (termination time) ===")
    if output_file_path is not None and output_file_path != "":
        save_run_stats(results, output_file_path)

    return results



def plot_travel_time(stats, title=None):
    if not title is None:
        title = f" ({title})"

    travel_times = chain.from_iterable([stat["collectors"][0]["travel_stats"] for stat in stats])
    travel_times = [travel_time[0] for travel_time in travel_times]

    sns.set_style("whitegrid")
    plt.hist(travel_times, bins=100)
    plt.xlim(0, max(travel_times))
    plt.xlabel("Travel time")
    plt.ylabel("Frequency")
    plt.title(f"Travel time distribution{title}")
    plt.tight_layout()
    plt.show()



def plot_crashes(avg_stats, title=None):
    if not title is None:
        title = f" ({title})"

    crashed_cars = avg_stats["crashed_cars"][0]

    sns.set_style("whitegrid")
    plt.pie([crashed_cars, avg_stats["departures"][0] - crashed_cars], labels=["Crashed", "Not crashed"],
            autopct='%1.1f%%')
    plt.title(f"Percentage of cars crashing{title}")
    plt.tight_layout()
    plt.show()


def plot_common_crash_locations(avg_stats, title=None):
    if not title is None:
        title = f" ({title})"

    crash_places = avg_stats["collision_places"]
    crash_places.sort(key=lambda x: x[1], reverse=True)
    crash_places = list(filter(lambda x: x[1] > 0, crash_places))

    sns.set_style("whitegrid")
    plt.pie([place[1] for place in crash_places], labels=[place[0] for place in crash_places], autopct='%1.1f%%')
    plt.title(f"Most common crash places{title}")
    plt.tight_layout()
    plt.show()
