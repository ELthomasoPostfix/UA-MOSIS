#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e ErrorA -sSrgv ../Diagrams/IntegrationMethods.drawio -E delta=0.1
import matplotlib.pyplot as plt

from IntegrationMethods import *

from util import runSimulation


def plotSimulation(fwd, bwd, trap, anal, duration, delta_t):
    # Plot all data on single axis
    fig, ax = plt.subplots()

    ax.plot(bwd[0], bwd[1], label='BWDEulerCalc')
    ax.plot(fwd[0], fwd[1], label='FWDEulerCalc')
    ax.plot(trap[0], trap[1], label='TrapezoidCalc')
    ax.plot(anal[0], anal[1], label='AnalyticCalc')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Approximation')

    plt.title(f"Integration Methods (t={duration}, Δt={delta_t})")
    plt.tight_layout()
    plt.legend()

    plt.show()


MODELS = [
    (BWDEulerCalc, "BWDEulerCalc"),
    (FWDEulerCalc, "FWDEulerCalc"),
    (TrapezoidCalc, "TrapezoidCalc"),
    (AnalyticCalc, "AnalyticCalc")
]
DURATION = 100
# DELTA_TIMES = [0.1, 0.01, 0.001]
DELTA_TIMES = [0.1]

for j, deltaT in enumerate(DELTA_TIMES):
    int_data = []
    for i, (model, param) in enumerate(MODELS):
        int_data.append(runSimulation(model(param), DURATION, deltaT, ['I'])[0])
    plotSimulation(*int_data, duration=DURATION, delta_t=deltaT)

