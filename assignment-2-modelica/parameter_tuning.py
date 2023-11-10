# This file contains example Python code to demonstrate the simulation of the newtonCooling Modelica model
# You need os package to execute commands in shell
import os
import csv
import numpy as np
from typing import List
from matplotlib import pyplot as plt
from scipy import io  # You need scipy package to read MAT-files
from util import readMat, meanSquaredError, GLOBALS, run_simulation
import seaborn as sns


def optimizeDrag() -> None:
    # Load comparison data
    refDisplacementData: List[float] = []
    with open("./assignment-files/deceleration_data.csv", "r") as referenceFile:
        reader = csv.reader(referenceFile)
        next(reader)  # Skip header
        refDisplacementData = [float(line[1]) for line in reader]

    # b in (0.00, 3.00]
    bRange = [bv for bv in np.arange(3.00, 0.00, -0.01)]
    mseList: List[float] = []
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

    minMSE: float = min(mseList)
    minMSEIndex: int = mseList.index(minMSE)
    minMSEBvalue: float = bRange[minMSEIndex]
    print("min mse ", minMSE)
    print("min mse idx ", minMSEIndex)
    print("min mse b-value ", minMSEBvalue)


if __name__ == "__main__":
    # GLOBALS.buildPlantModel()
    optimizeDrag()