#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e PIDController -sSrgv ../Diagrams/PIDController.drawio

from PIDController import *
from pyCBD.scheduling import TopologicalScheduler
from pyCBD.depGraph import createDepGraph

from pyCBD.converters.latexify import CBD2Latex

cbd = PIDController("PIDController")

depGraph = createDepGraph(cbd, 0)
scheduler = TopologicalScheduler()
sortedGraph = scheduler.obtain(depGraph, 1, 0.0)

print(depGraph)

print("=" * 200)

print(sortedGraph)


print("+" * 200)

flat_cbd = cbd.flattened()

depGraph = createDepGraph(flat_cbd, 0)
scheduler = TopologicalScheduler()
sortedGraph = scheduler.obtain(depGraph, 1, 0.0)

print(depGraph)

print("=" * 200)

print(sortedGraph)

