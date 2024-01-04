import json

from components.crossroads import CrossRoads, ROWCrossRoads, RoundaboutCrossRoads
from other.sim_utils import run_cw_simulation
from other.helpers import dict_stat


# avg_stats = []
# for crossroad_type in [ROWCrossRoads, RoundaboutCrossRoads]:
#     stats = []
#     for i in range(10):
#         # This kills ROW: IAT_min=5.0, IAT_max=10.0,
#         stats.append(
#             run_cw_simulation(10_000, verbose=False, crossroad_type=crossroad_type, branch_segment_amount=1, limit=100,
#                               print_stats=True, ))
#     averaged_stats = dict_stat(stats)
#     avg_stats.append(averaged_stats)
#
#     print(f"Type: {crossroad_type.__name__}")
#
#     print(json.dumps(averaged_stats, indent=4))
#
# # # Print crash rate for every crossroad type
# for i, crossroad_type in enumerate([CrossRoads, ROWCrossRoads, RoundaboutCrossRoads]):
#     print(f"Type: {crossroad_type.__name__}   Crash rate: {avg_stats[i]['crash_rate'][0] * 100:.2f}% +- {avg_stats[i]['crash_rate'][1] * 100:.2f}%")


run_cw_simulation(10_000, verbose=False, crossroad_type=ROWCrossRoads, limit=100, output_file_path="crossroads.json",
                  draw_dot=True)
