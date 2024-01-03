from other.sim_utils import run_cw_simulation

from components.crossroads import CrossRoads, ROWCrossRoads, RoundaboutCrossRoads

for crossroad_type in [CrossRoads, ROWCrossRoads, RoundaboutCrossRoads]:
    num_crashes = []
    for i in range(20):
        num_crashes.append(run_cw_simulation(10_000, verbose=False, crossroad_type=crossroad_type, branch_segment_amount=1,
                                             IAT_min=5.0, IAT_max=10.0,
                                             limit=100, output_file_path="crossroads.json"))

    print(f"Type: {crossroad_type.__name__}")
    print(f"Crashes: {num_crashes}")
    print(f"Average crashes: {sum(num_crashes) / len(num_crashes)}")


# run_cw_simulation(10_000, verbose=False, crossroad_type=RoundaboutCrossRoads, limit=100, output_file_path="crossroads.json",
#                   draw_dot=True)
