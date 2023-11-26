# Causal Block Diagrams (cbd)

This directory pertains to the third assignment about Causal Block Diagrams for the MOSIS course. 
You can find the original assignment in html format, as well many of the code, test and example files linked to by the assignment, in the directory of this assignment. Though inclusion of these files inflates the size of the repo, we believe all required files should be available upon cloning.


# Structure
The three parts of the assignment are in their own subdirectories, with the following structure.

```sh
assignment-3-cbd/
├── harmonic-oscillator/
│   ├── graphs/
│   ├── HarmonicOscillator.drawio
│   ├── HarmonicOscillator.py
│   ├── HarmonicOscillator_experiment.py
├── integration-methods/
│   ├── graphs/
│   ├── IntegrationMethods.drawio
│   ├── IntegrationMethods.py
│   ├── IntegrationMethods_experiment.py
└── inline-integration/
    ├── graphs/
    ├── template-fmu/ (Jinja template for FMU conversion)
    ├── output-fmu/ (Output FMU used for PID.fmu generation)
    ├── fmu-outputs/ (All FMUs used for simulating the model)
    │
    ├── CBD2FMU.py (Script for converting CBD to FMU)
    ├── compile_and_run.py (Script for combining FMUs and simulating them)
    ├── PIDController.drawio (CBD implementation of the PID controller)
    ├── PIDController.py
    ├── PIDController_experiment.py
    └── PCarController.mo (Adapted modelica model for the car controller without PID)
 

# Setup

To run python scripts, a virtual environment must be setup with the needed packages. The needed steps follow.

Enter the subdirectory for assignment 2 from the root directory.
```sh
cd assignment-3-cbd/
```

Create the venv.
```sh
python -m venv venv
```

activate the venv.
```sh
# Windows
./venv/scripts/activate

# Linux
source ./venv/bin/activate
```

Install dependencies in local venv.
```sh
pip install -r requirements.txt
```

It is also needed to install the pyCBD framework.

```sh
# Enter the directory holding the pyCBD framework
cd ./CBD/src/
# Install the pyCBD framework using its setup.py file
python3 -m pip install .
```

## Problems

For the task on *Inline Integration (and Cosimulation)*, we encountered some problems regarding running the `compile_and_run.py` script. We had to install VSCode build tools, from [here](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2019) under *Tools for Visual Studio* > *Build Tools for Visual Studio 2022*.

# Assignment Requirements

This assignment should make use of [Python 3.6+](https://www.python.org/).