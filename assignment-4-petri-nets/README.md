# Petri Nets

This directory pertains to the fourth assignment about petri nets for the MOSIS course. 
You can find the original assignment in html format, as well many of the code, test and example files linked to by the assignment, in the `assignment-files` subdirectory ([here](/assignment-4-petri-nets/assignment-files/)). Though inclusion of these files inflates the size of the repo, we believe all required files should be available upon cloning.

This is a late submission, the original report found as `old_report.pdf`, the new one is `report.pdf`

# TAPAAL binaries

We provide the binaries of TAPAAL that we used to solve this assignment in this git repo as `.zip` files. They are located in the [assignment-files directory](/assignment-4-petri-nets/assignment-files/). **However**, these binaries are *included in the `.gitignore`* file of the assignment 4 directory, to reduce the size of the initially cloned repo.

# Assignment Requirements

This assignment should make use of [Python 3.6+](https://www.python.org/).

# Project directory
Our submission archive is structured as follows:
- `/analysis/`:  Contains the generated reachability and coverability dot files
- `/assignment-files/`: Assignement description, and provided images and scripts
- `/diagrams/`: Cleaned up DrawIO diagrams of the TAPAAL models
  - `/building-blocks/`: Basic structures used to form the models
  - `/invariant-visualisation/`: Visualisation of the invariant paths
  - `/roundabout-basic/`: Roundabout without the clock system
  - `/v1/`: First attempt at clocked roundabout
  - `/v3/`: Final clocked roundabout solution
- `/graphs/`: Generated coverability and reachability graphs
- `/models/`: Contains all TAPAAL models generated for completing the tasks
- `/report/`: Folder that contains the report(s)
- `/traces/`: All simulation traces generated for completing the tasks
