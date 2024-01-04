import json

from components.crossroads import CrossRoads, ROWCrossRoads, RoundaboutCrossRoads
from other.sim_utils import run_cw_simulation, plot_travel_time, plot_crashes, plot_common_crash_locations
from other.helpers import dict_stat



#                               L: float = 10.0, L_cr: float = 5, v_max: float = 12.0
#         IAT_min: float = 10.0, IAT_max: float = 18.5, v_pref_mu: float = 15.0, v_pref_sigma: float = 1.0,
#         limit: int = 10, observ_delay: float = 0.1,
#

avg_stats = []
for crossroad_type in [CrossRoads]:
    stats = []
    for i in range(10):
        stats.append(
            run_cw_simulation(10_000, verbose=False, crossroad_type=crossroad_type,
                              branch_count=4, branch_segment_amount=3, limit=100,
                              L=10.0, L_cr=5.0, IAT_min=10.0, IAT_max=15.0,
                              v_max=30.0, v_pref_mu=25.0, v_pref_sigma=5.0,
                              print_stats=False, ))
    averaged_stats = dict_stat(stats)
    avg_stats.append(averaged_stats)

    print(f"Type: {crossroad_type.__name__}")

    print(json.dumps(averaged_stats, indent=4))

# # Print crash rate for every crossroad type
for i, crossroad_type in enumerate([CrossRoads]):
    avg_stat = avg_stats[i]

    plot_travel_time(stats, crossroad_type.__name__)
    plot_crashes(avg_stat, crossroad_type.__name__)
    plot_common_crash_locations(avg_stat, crossroad_type.__name__)

    print(f"Type: {crossroad_type.__name__}\n{json.dumps(avg_stat, indent=4)}")



# for i in range(1000):
#     run_cw_simulation(10_000, verbose=False, crossroad_type=ROWCrossRoads, limit=2, output_file_path="crossroads.json",
#                       draw_dot=False)
