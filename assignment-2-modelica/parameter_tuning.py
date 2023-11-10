# This file contains example Python code to demonstrate the simulation of the newtonCooling Modelica model
# You need os package to execute commands in shell
import os
import csv
import numpy as np
from typing import List, Tuple, Any
from matplotlib import pyplot as plt
from scipy import io  # You need scipy package to read MAT-files
from util import readMat, meanSquaredError, GLOBALS, run_simulation
import seaborn as sns


def optimizeDrag(refDisplacementData: List[float]) -> tuple[list[Any], list[float], list[list[float]], Any]:
    # b in (0.00, 3.00]
    bRange = [bv for bv in np.arange(3.00, 0.00, -0.01)]
    mseList: List[float] = []
    displacementDatas: List[List[float]] = []

    for bValue in bRange:
        timeData, displacementData = run_simulation(
            "plant",
            {"A": 60, "b": bValue, "M": 1500, "u": 0},
            ["time", "x"]
        )

        # Manually fix duplicate final simulation value
        timeData = timeData[:len(timeData) - 1]
        displacementData = displacementData[:len(displacementData) - 1]

        mseList.append(meanSquaredError(refDisplacementData, displacementData))
        displacementDatas.append(displacementData)

    minMSE: float = min(mseList)
    minMSEIndex: int = mseList.index(minMSE)
    minMSEBvalue: float = bRange[minMSEIndex]
    print("min mse ", minMSE)
    print("min mse idx ", minMSEIndex)
    print("min mse b-value ", minMSEBvalue)

    return bRange, mseList, displacementDatas, timeData


def plotDrag(bRange: list[Any], mseList: list[float]) -> None:
    sns.set_style("whitegrid")

    plt.plot(bRange, mseList)
    plt.xlabel("Drag coefficient b")
    plt.ylabel("MSE")
    plt.title("MSE over drag coefficient b")

    # Hide grid
    plt.grid(False)

    # Mark minimum MSE
    minMSE: float = min(mseList)
    minMSEIndex: int = mseList.index(minMSE)
    minMSEBvalue: float = bRange[minMSEIndex]
    plt.plot(minMSEBvalue, minMSE, color="#082234")

    # Annotate minimum MSE with dark blue dot, and arrow coming from north
    plt.annotate(
        f"(b={round(minMSEBvalue, 2)}, MSE={round(minMSE, 2)})",
        xy=(minMSEBvalue, minMSE),
        xytext=(minMSEBvalue, minMSE + 24000),
        arrowprops=dict(facecolor="#082234", shrink=0.05),
    )

    # Set ylim to 0
    plt.ylim(bottom=0)

    # Save figure
    plt.savefig("drag-optimization.png")

    plt.show()


def plotDisplacement(displacementDatas: list[float], refDisplacementData: list[float], timeData: list[float]) -> None:
    sns.set_style("whitegrid")

    # Dotted style and bigger linewidth
    plt.plot(timeData, displacementDatas, label="Model", alpha=0.5, color="#709CB5")
    plt.plot(timeData, refDisplacementData, label="Reference", linestyle=":", linewidth=3, color="#3C2850")

    plt.xlabel("Time (s)")
    plt.ylabel("Displacement (m)")
    plt.title("Displacement over time")

    plt.legend()
    plt.legend(["Modelled displacement", "Referenced displacement"])

    plt.grid(False)

    plt.savefig("displacement-model-ref.png")

    plt.show()


if __name__ == "__main__":
    GLOBALS.buildPlantModel()

    # Load comparison data
    refDisplacementData: List[float] = []
    with open("./assignment-files/deceleration_data.csv", "r") as referenceFile:
        reader = csv.reader(referenceFile)
        next(reader)  # Skip header
        refDisplacementData = [float(line[1]) for line in reader]

    bRange, mseList, displacementDatas, timeData = optimizeDrag(refDisplacementData)

    minBErrorIndex: int = mseList.index(min(mseList))
    minDisplacementData: List[float] = displacementDatas[minBErrorIndex]

    plotDisplacement(minDisplacementData, refDisplacementData, timeData)

    plotDrag(bRange, mseList)
