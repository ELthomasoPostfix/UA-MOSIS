import json

from other.sim_utils import run_rs_simulation
from other.helpers import dict_stat


# Long simulation
stats = []
for i in range(5):
    stats.append(run_rs_simulation(5_000_000, verbose=False, limit=4_000, print_stats=False))

print(json.dumps(dict_stat(stats), indent=4))


# run_rs_simulation(5_000_000, limit=4_000, output_file_path="roadstretch_long.json")
