#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e BWDEulerCalc -sSrgv ./integration-methods/IntegrationMethods.drawio -d ./integration-methods
# The file has since been modified by hand for better plotting.

import matplotlib.pyplot as plt

from IntegrationMethods import *

import sys
sys.path.append('..')

from cbd_util import runSimulation, processData


def plotSimulation(data, duration, delta_t, y_label):
    # Plot all data on single axis
    fig, ax = plt.subplots()

    for (values, label) in data:
        if label == "Analytic":
            ax.plot(values[0], values[1], label=label, linestyle='dashed', alpha=0.5, linewidth=3)
        else:
            ax.plot(values[0], values[1], label=label)

    ax.grid(True, axis='y')

    ax.set_xlabel('Time (s)')
    ax.set_ylabel(y_label)

    plt.title(f"Integration Methods (t={duration}, Δt={delta_t})")
    plt.tight_layout()
    plt.legend()


    plt.savefig(f"./graphs/integration_methods_t{duration}_dt{delta_t}.png")
    plt.show()


MODELS = [
    (BWDEulerIntCalc, "BWDEulerIntCalc"),
    (FWDEulerIntCalc, "FWDEulerIntCalc"),
    (TrapezoidIntCalc, "TrapezoidIntCalc"),
    (AnalyticIntCalc, "AnalyticIntCalc")
]
DURATION = 100
DELTA_TIMES = [0.1, 0.01, 0.001]
# DELTA_TIMES = [0.1]


model_name = {
    BWDEulerIntCalc: "Backward Euler",
    FWDEulerIntCalc: "Forward Euler",
    TrapezoidIntCalc: "Trapezoid",
    AnalyticIntCalc: "Analytic"
}

for j, deltaT in enumerate(DELTA_TIMES):
    integration_data = []
    for i, (model, param) in enumerate(MODELS):
        values = runSimulation(model(param), DURATION, deltaT, ['I'])[0]
        integration_data.append((values, model_name[model]))
    plotSimulation(integration_data, duration=DURATION, delta_t=deltaT, y_label="Approximation")

    reference_data = integration_data.pop(-1)

    error_data = []
    for i, (values, label) in enumerate(integration_data):
        error_values = [values[0], [abs(x - y) for x, y in zip(values[1], reference_data[0][1])]]
        error_data.append((error_values, label))

        print(f"{label} (Δt={deltaT}): {error_values[1][-1]}")
        print(f"  Max: {max(error_values[1])}")
        print(f"  Cumulative: {sum(error_values[1])}")


    plotSimulation(error_data, duration=DURATION, delta_t=deltaT, y_label="Error")
