import json

from other.sim_utils import run_rs_simulation
from other.helpers import dict_avg



# Short simulation
stats = []
for i in range(50):
    stats.append(run_rs_simulation(20_000, verbose=False, limit=200, IAT_min=5.0, IAT_max=10.0, print_stats=False))

print(json.dumps(dict_avg(stats), indent=4))


# run_rs_simulation(20_000, verbose=True, limit=200, IAT_min=5.0, IAT_max=10.0, output_file_path="roadstretch_short.json")