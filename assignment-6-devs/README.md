# DEVS
This directory pertains to the sixth assignment about DEVS for the MOSIS course. 
You can find the original assignment in html format, as well many of the code, test and example files linked to by the assignment, in the `assignment-files` subdirectory ([here](/assignment-6-devs/assignment-files/)). Though inclusion of these files inflates the size of the repo, we believe all required files should be available upon cloning.


# Assignment Requirements
This assignment should make use of [Python 3.6+](https://www.python.org/).


# Project directory
Our submission archive is structured as follows:
- `/assignment-files/`: Assignement description, and provided images and scripts
- `/report/`: Folder that contains the report(s)

# Structure

The project structure, w.r.t. the DEVS code files, should look as follows once all [setup steps](#setup) have been successfully completed.

```sh
assignment-6-devs/
├── components/
│   ├── __init__.py
│   ├── collector.py
│   ├── crossroads.py
│   ├── fork.py
│   ├── gasstation.py
│   ├── generator.py
│   ├── messages.py
│   ├── roadsegment.py
│   └── sidemarker.py
├── experiments/
│   ├── __init__.py
│   └── ...
├── other/
│   ├── ...
├── PythonPDEVS-master/
│   └── pythonpdevs/
│       └── ...
├── tests/
│   ├── __init__.py
│   └── ...
├── venv/   (optional)
└── __init__.py
```

Note that the contents of the `assignment-6-devs/other/` and the `assignment-6-devs/experiments/` directories are not exhaustively listed in the structure description below. This is because the contents may fluctuate, both in number and filenames.


# Setup

First and foremost, you might want to set up a virtual environment.

```sh
python3 -m venv venv
source venv/bin/activate    # linux
./venv/Scripts/activate     # windows
```

Then install the project requirements from the `assignment-6-devs` directory.

```sh
pip install -r requirements.txt
```

Next, check if the `PythonPDEVS-master` directory is found at `assignment-6-devs/` -- the root of this assignment subproject. If it is not, then locate the similarly named `.zip` in the [assignment-files directory](/assignment-6-devs/assignment-files/). Copy the archive and paste it one level up, then unzip it.

The `PythonPDEVS-master` directory is now present. Install it (as according to the [documentation](https://msdl.uantwerpen.be/documentation/PythonPDEVS/installation.html)):

```sh
cd PythonPDEVS-master/pythonpdevs/src/
# IF using virtual environment
python3 setup.py install
# ELSE
python3 setup.py install --user
# (optional) check if pypdevs installed properly
cd ../../../
python3 -c "import pypdevs"
```

# Running

_Do not forget to activate the virtual environment, if you created one!_

Running the DEVS models is done from the `assignment-6-devs` directory through the *experiments* found in the [experiment directory](/assignment-6-devs/experiments/).

```sh
python3 -m experiments.experiment
```

A set of *test benchmarks* was also provided with the assignment, to test the validity of our solution. To run them, call the following command from the `assignment-6-devs` directory.

```sh
python3 -m unittest discover -v
```
