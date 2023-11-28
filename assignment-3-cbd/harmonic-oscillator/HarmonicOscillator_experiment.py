#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e ErrorA -sSrgv ./harmonic-oscillator/HarmonicOscillator.drawio -d ./harmonic-oscillator
# The file has since been modified by hand for better plotting.

from HarmonicOscillator import *

import matplotlib.pyplot as plt
import seaborn as sns

import sys
sys.path.append('../')

from cbd_util import runSimulation

sns.set_style("whitegrid")


def plotSimulation(name, xapprox, xtrue, error, duration, delta_t):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    # Only add y-axis grids
    ax1.grid(True, axis='y', alpha=0.5)
    ax2.grid(True, axis='y', linestyle='dashed', alpha=0.5)

    # Disable x-axis grids
    ax1.grid(False, axis='x')
    ax2.grid(False, axis='x')

    ax2.plot(error[0], error[1], color='red', label='error', alpha=0.5, linewidth=3)
    ax1.plot(xapprox[0], xapprox[1], color='green', label='x')
    ax1.plot(xtrue[0], xtrue[1], color='blue', label='sinT')

    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Displacement')
    ax2.set_ylabel('Error', color='red')

    ax2.tick_params(axis='y', labelcolor='red')


    ax1.fill_between(xapprox[0], xapprox[1], xtrue[1], color='red',  alpha=0.2)

    # Combine legends and add custom labels
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, ['Approx', 'True', 'Error'], loc='upper left')

    plt.title(f"{name} Oscillator (t={duration}, Δt={delta_t})")
    plt.tight_layout()

    plt.savefig(f"./graphs/{name}_oscillator_t{duration}_dt{delta_t}.png")
    plt.show()




CBD_MODELS = [
    (ErrorA, "ErrorA"),
    (ErrorB, "ErrorB")
]
DURATION = 50
# DELTA_TIMES = [0.1, 0.01, 0.001]
DELTA_TIMES = [0.1]

# Iterate over every model, and then simulate the model for every deltaT (and plot the results)
for i, (model, param) in enumerate(CBD_MODELS):
    for j, deltaT in enumerate(DELTA_TIMES):
        approx, true, error = runSimulation(model(param), DURATION, deltaT, ['xt', 'sinT', 'et'])
        plotSimulation(param, approx, true, error, DURATION, deltaT)

        print(f"{param} (Δt={deltaT}): {error[1][-1]}")