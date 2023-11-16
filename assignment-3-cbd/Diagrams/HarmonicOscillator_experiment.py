#!/usr/bin/python3
# This file was automatically generated from drawio2cbd with the command:
#   A:\Python\UA-MOSIS\assignment-3-cbd\DrawioConvert\__main__.py -F CBD -e error -sSrgv ../Diagrams/HarmonicOscillator.drawio -E delta=0.1

from HarmonicOscillator import *

import matplotlib.pyplot as plt
import seaborn as sns

from util import runSimulation

sns.set_style("whitegrid")


def plotSimulation(name, xapprox, xtrue, error, duration, delta_t):
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    ax1.plot(xapprox[0], xapprox[1], color='green', label='x')
    ax1.plot(xtrue[0], xtrue[1], color='blue', label='sinT')
    ax2.plot(error[0], error[1], color='red', label='error')

    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Approximation')
    ax2.set_ylabel('Error', color='red')

    ax1.yaxis.grid(True, linestyle='dotted')
    ax1.xaxis.grid(False)

    ax1.fill_between(xapprox[0], xapprox[1], xtrue[1], color='red',  alpha=0.2)

    plt.title(f"{name} Oscillator (t={duration}, Δt={delta_t})")
    plt.tight_layout()

    plt.show()

CBD_MODELS = [
    (ErrorA, "ErrorA"),
    (ErrorB, "ErrorB")
]
DURATION = 50
DELTA_TIMES = [0.1, 0.01, 0.001]

for i, (model, param) in enumerate(CBD_MODELS):
    for j, deltaT in enumerate(DELTA_TIMES):
        approx, true, error = runSimulation(model(param), DURATION, deltaT, ['xt', 'sinT', 'et'])
        plotSimulation(param, approx, true, error, DURATION, deltaT)
