import json

from other.sim_utils import run_rs_simulation
from other.helpers import dict_avg


# Long simulation
stats = []
for i in range(5):
    stats.append(run_rs_simulation(5_000_000, verbose=False, limit=4_000, IAT_min=10.0, IAT_max=30.0, print_stats=False))

print(json.dumps(dict_avg(stats), indent=4))



# Short simulation
stats = []
for i in range(30):
    stats.append(run_rs_simulation(20_000, verbose=False, limit=200, IAT_min=10.0, IAT_max=30.0, print_stats=False))

print(json.dumps(dict_avg(stats), indent=4))


# run_rs_simulation(5_000_000, limit=4_000, output_file_path="roadstretch_long.json")
