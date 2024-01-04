import json

from other.sim_utils import run_rs_simulation, plot_travel_time, plot_crashes, plot_common_crash_locations
from other.helpers import dict_stat

# Short simulation
stats = []
for i in range(30):
    stats.append(run_rs_simulation(200_000,#00,
                                   generator_segment_count=10,
                                   collector_segment_count=10,
                                   verbose=False, limit=1000, print_stats=False,
                                   L_upper=10.0, L_lower=5.0, L_conn=5.0,
                                   v_max=30.0, v_max_gas=20.0,
                                   IAT_min=10.0, IAT_max=15.0,
                                   v_pref_mu=25.0, v_pref_sigma=5.0,
                                   output_file_path="roadstretch_short.json"
                                   ))

avg_stats = dict_stat(stats)
print(json.dumps(avg_stats, indent=4))


plot_travel_time(stats)
plot_crashes(avg_stats)
plot_common_crash_locations(avg_stats)


# stat = run_rs_simulation(20_000, verbose=False, limit=200, IAT_min=5.0, IAT_max=10.0, output_file_path="roadstretch_short.json")
# print(json.dumps(stat, indent=4))