#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e ErrorA -sSrgv ../Diagrams/IntegrationMethods.drawio -E delta=0.1
import matplotlib.pyplot as plt

from IntegrationMethods import *

from util import runSimulation, processData


def plotSimulation(data, duration, delta_t):
    # Plot all data on single axis
    fig, ax = plt.subplots()

    for (values, label) in data:
        ax.plot(values[0], values[1], label=label)

    ax.grid(True)

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Approximation')

    plt.title(f"Integration Methods (t={duration}, Δt={delta_t})")
    plt.tight_layout()
    plt.legend()

    plt.show()


# model = AnalyticFuncCalc("AnalyticFuncCalc")
# data = runSimulation(model, 100, 0.1, ['y'])[0]
#
# # Plot data
# fig, ax = plt.subplots()
# ax.plot(data[0], data[1], label='AnalyticFuncCalc')
# ax.set_xlabel('Time (s)')
# ax.set_ylabel('Value')
#
# # Ylim
# ax.set_ylim([-0.02, 0.15])
# ax.set_xlim([0, 100])
#
# # Show gridlines
# ax.grid(True)
#
# plt.title(f"Analytic Function (t=100, Δt=0.1)")
# plt.tight_layout()
# plt.show()
#


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
    integration_data = []
    for i, (model, param) in enumerate(MODELS):
        values = runSimulation(model(param), DURATION, deltaT, ['I'])[0]
        integration_data.append((values, model.__name__))
    plotSimulation(integration_data, duration=DURATION, delta_t=deltaT)

    reference_data = integration_data.pop(-1)

    error_data = []
    for i, (values, label) in enumerate(integration_data):
        error_values = [values[0], [abs(x - y) for x, y in zip(values[1], reference_data[0][1])]]
        error_data.append((error_values, label))

    plotSimulation(error_data, duration=DURATION, delta_t=deltaT)
