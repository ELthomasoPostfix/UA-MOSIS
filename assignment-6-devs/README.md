# DEVS
This directory pertains to the sixth assignment about DEVS for the MOSIS course. 
You can find the original assignment in html format, as well many of the code, test and example files linked to by the assignment, in the `assignment-files` subdirectory ([here](/assignment-6-devs/assignment-files/)). Though inclusion of these files inflates the size of the repo, we believe all required files should be available upon cloning.


# Assignment Requirements
This assignment should make use of [Python 3.6+](https://www.python.org/).


# Project directory
Our submission archive is structured as follows:
- `/assignment-files/`: Assignement description, and provided images and scripts
- `/report/`: Folder that contains the report(s)


# Setup

First and foremost, you might want to set up a virtual environment.

```sh
python3 -m venv venv
source venv/bin/activate    # Assumes linux
```

Next, check if the `PythonPDEVS-master` directory is found at the root of this assignment subproject. If it is not, then locate the similarly named `.zip` in the [assignment-files directory](/assignment-6-devs/assignment-files/). Copy the archive and paste it one level up, then unzip it.

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