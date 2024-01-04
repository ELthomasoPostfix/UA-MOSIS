import json

from other.sim_utils import run_rs_simulation
from other.helpers import dict_stat

from matplotlib import pyplot as plt
import seaborn as sns
from itertools import chain

# Short simulation
# stats = []
# for i in range(30):
#     stats.append(run_rs_simulation(200_000, verbose=False, limit=100, print_stats=False,
#                                    L_upper=1600.0, L_lower=100.0, L_conn=100.0,
#                                    v_max=16.0, v_max_gas=5.0,
#                                    IAT_min=60.0, IAT_max=100.0, v_pref_mu=10.0, v_pref_sigma=1.5,
#                                    ))
#
# avg_stats = dict_stat(stats)
# print(json.dumps(avg_stats, indent=4))
#
# # travel_times = [stat["collector"]["travel_stats"] for stat in stats]
# travel_times = chain.from_iterable([stat["collectors"][0]["travel_stats"] for stat in stats])
# travel_times = [travel_time[0] for travel_time in travel_times]
#
# # Plot travel times as histogram
# sns.set_style("whitegrid")
# plt.hist(travel_times, bins=100)
# plt.xlim(0, max(travel_times))
# # plt.ylim(0, plt.ylim()[1] / len(stats))
# plt.show()
#
# # Plot percentage of cars crashing as piechart
# crashed_cars = avg_stats["crashed_cars"][0]
#
# sns.set_style("whitegrid")
# plt.pie([crashed_cars, avg_stats["departures"][0] - crashed_cars], labels=["Crashed", "Not crashed"], autopct='%1.1f%%')
# plt.show()


# travel_times = [stat["collector"]["travel_stats"] for stat in stats]
travel_times = chain.from_iterable([stat["collectors"][0]["travel_stats"] for stat in stats])
travel_times = [travel_time[0] for travel_time in travel_times]

# Plot travel times as histogram
sns.set_style("whitegrid")
plt.hist(travel_times, bins=100)
plt.xlim(0, max(travel_times))
plt.xlabel("Travel time")
plt.ylabel("Frequency")
plt.title("Travel time distribution")
plt.tight_layout()
plt.show()

# Plot percentage of cars crashing as piechart
crashed_cars = avg_stats["crashed_cars"][0]

sns.set_style("whitegrid")
plt.pie([crashed_cars, avg_stats["departures"][0] - crashed_cars], labels=["Crashed", "Not crashed"], autopct='%1.1f%%')
plt.title("Percentage of cars crashing")
plt.tight_layout()
plt.show()

# Plot pie chart with most common crash places, it is a [(place, count)] list
crash_places = avg_stats["collision_places"]
crash_places.sort(key=lambda x: x[1], reverse=True)
crash_places = list(filter(lambda x: x[1] > 0, crash_places))

sns.set_style("whitegrid")
plt.pie([place[1] for place in crash_places], labels=[place[0] for place in crash_places], autopct='%1.1f%%')
plt.title("Most common crash places")
plt.tight_layout()
plt.show()



# stat = run_rs_simulation(20_000, verbose=False, limit=200, IAT_min=5.0, IAT_max=10.0, output_file_path="roadstretch_short.json")
# print(json.dumps(stat, indent=4))