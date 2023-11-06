# modelica

This directory pertains to the second assignment, modelica for the MOSIS course. You can find the original assignment in both html and pdf formats, as well many of the code, test and example files linked to by the assignment, in the `assignment-files` subdirectory ([here](/assignment-2-modelica/assignment-files/)). Though inclusion of these files inflates the size of the repo, we believe all required files should be available upon cloning.

Somewhat counter to the claim we just made, an example modelica model's zip archive provided for this assignment proved a little too large (110 MB), despite it not being required for solving it. We do add its [download link](http://msdl.uantwerpen.be/people/hv/teaching/MoSIS/assignments/Modelica/example.zip).

# Task 2

Task 2 pertains to estimating the drag coeficient parameter of the plant model. The given [csv file download link](http://msdl.uantwerpen.be/people/hv/teaching/MoSIS/assignments/Modelica/deceleration_data.csv) contains "real-world" measurement data on the plant given specific initial values.

The file [simulate.py](/assignment-2-modelica/assignment-files/simulate.py) in `assignment-files` was taken from the [example zip download link](http://msdl.uantwerpen.be/people/hv/teaching/MoSIS/assignments/Modelica/example.zip) provided in the assignment. The file [task_2_simulate.py](/assignment-2-modelica/task_2_simulate.py) was based on the file in `assignment-files`.

# Setup

Before a sweep run can be done using python, we need to generate the compiled model. To do this, we need to

1) change OMEdit settings:
    * set `Tools > Options > General > Working Directory` to `.../assignment-2-modelica/`
    * disable `Tools > Options > Simulation > Delete entire simulation directory of the model when OMEdit is closed`
2) verify and run a single simulation for the desired model

To run the python script, a virtual environment must be setup with the needed packages. The needed steps follow.

Enter the subdirectory for assignment 2 from the root directory.
```sh
cd assignment-2-modelica/
```

Create the venv.
```sh
python -m venv venv
```

activate the venv.
```sh
./venv/scripts/activate
```

Install dependencies in local venv.
```sh
pip install -r requirements.txt
```

# Run

To run the model for the specified parameters, simply call the python file [task_2_simulate.py](/assignment-2-modelica/task_2_simulate.py) **from the where the compiled Modelica model is located**. It *must* be called from there because the needed IO operations are hardcoded into the python file. The [Setup section](#setup) specified this to be [assignment-2-modelica/](/assignment-2-modelica/).

```sh
python task_2_simulate.py
```

# Assignment Requirements

This assignment should make use of [Python 3.6+](https://www.python.org/).