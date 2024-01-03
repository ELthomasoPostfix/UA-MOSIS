from other.sim_utils import run_rs_simulation



# Short simulation

# num_crashes = []
# for i in range(100):
#  num_crashes.append(run_rs_simulation(20_000, verbose=False, limit=200, IAT_min=5.0, IAT_max=10.0,
#                                       output_file_path="roadstretch_short.json"))
#
# print(num_crashes)
# print(sum(num_crashes) / len(num_crashes))

run_rs_simulation(20_000, verbose=True, limit=200, IAT_min=5.0, IAT_max=10.0, output_file_path="roadstretch_short.json")