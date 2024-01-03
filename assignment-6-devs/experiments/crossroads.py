import json

from components.crossroads import CrossRoads, ROWCrossRoads, RoundaboutCrossRoads
from other.sim_utils import run_cw_simulation
from other.helpers import dict_avg



# for crossroad_type in [CrossRoads, ROWCrossRoads, RoundaboutCrossRoads]:
#     stats = []
#     for i in range(10):
#         stats.append(run_cw_simulation(10_000, verbose=False, crossroad_type=crossroad_type, branch_segment_amount=1,
#                                              IAT_min=5.0, IAT_max=10.0,
#                                              limit=100, output_file_path="crossroads.json"))
#
#     print(f"Type: {crossroad_type.__name__}")
#
#     print(json.dumps(dict_avg(stats), indent=4))




run_cw_simulation(10_000, verbose=False, crossroad_type=ROWCrossRoads, limit=100, output_file_path="crossroads.json",
                  draw_dot=True)
