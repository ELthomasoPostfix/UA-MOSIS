# This file contains example Python code to demonstrate the simulation of the newtonCooling Modelica model
# You need os package to execute commands in shell
import os
import csv
import numpy as np
from typing import List
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
from util import readMat, carCollided, GLOBALS

def singleSimulation(Kp: float, Ki: float, Kd: float) -> [List[float], List[float], List[float]]:
    """Perform a single simulation using the model binary.

    :param Kp: The proportional gain
    :param Ki: The integral gain
    :param Kd: The derivative gain
    :return: (timestamp list, lead car distance list, plant car distance list)
    """
    os.chdir(GLOBALS.outputDirName(GLOBALS.packageName, GLOBALS.controllerModelName))
    # OS-agnostic executable call
    # Executing the simulation ONLY works iff.
    #   1) the .bat file is called
    #   2) the call happens where the .bat file is located
    #   3) OMEdit is turned off (or at least does not have the model file opened?)
    # ==> This is windows specific, ubuntu users are on their own :(
    os.system(f".\{GLOBALS.controllerModelName}.bat -override Kp_start={Kp},Ki_start={Ki},Kd_start={Kd}")

    # Obtain the variable values by reading the MAT-file
    names, data = readMat(GLOBALS.outputFilePath(GLOBALS.packageName, GLOBALS.controllerModelName))
    os.chdir("..")  # Reset dir for next calls

    timeData: List[float] = data[names.index("time")]
    leadCarDistanceData: List[float] = data[names.index("lead_car.y")]
    plantCarDistanceData: List[float] = data[names.index("Plant.y")]

    return timeData, leadCarDistanceData, plantCarDistanceData


def plotGains() -> None:
    KpList = [0, 1, 20]
    KiList = [0, 1, 20]
    KdList = [0, 20, 40]

    # Create 3 x 9 subplots (with columns of 3 grouped)
    fig, ax = plt.subplots(3, 9, figsize=(100, 20))
    KpIdx, KiIdx, KdIdx = 0, 0, 0

    # Plot every 3x3 combination of gains in a 3x3 subplot
    for Kp in KpList:
        KiIdx = 0
        for Ki in KiList:
            KdIdx = 0
            for Kd in KdList:
                timeData, leadCarDistanceData, plantCarDistanceData = singleSimulation(Kp, Ki, Kd)

                collided, collision_idx = carCollided(leadCarDistanceData, plantCarDistanceData)

                column_idx = (KpIdx * 3) + KdIdx
                row_idx = KiIdx - 1

                # Combine lead car and plant car data into a single graph
                df = pd.DataFrame({'time': timeData, 'lead_car.y': leadCarDistanceData, 'plant_car.y': plantCarDistanceData})
                melted = pd.melt(df, id_vars=['time'], value_vars=['lead_car.y', 'plant_car.y'])
                # Calculate axis location in (3x9) grid
                sns.lineplot(x='time', y='value', hue='variable', data=melted, ax=ax[row_idx][column_idx])
                ax[row_idx][column_idx].set_title(f'Kp={Kp}, Ki={Ki}, Kd={Kd}')
                ax[row_idx][column_idx].set_xlabel('time (seconds)')
                ax[row_idx][column_idx].set_ylabel('distance (meters)')
                ax[row_idx][column_idx].legend().set_visible(False)

                # Add collision indicator to graph
                if collided:
                    ax[row_idx][column_idx].axvline(x=timeData[collision_idx], color='r', linestyle='--')

                KdIdx += 1
            KiIdx += 1
        KpIdx += 1

    # Add legend to last subplot
    ax[2][8].legend().set_visible(True)
    plt.show()


# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop ove the combinations of parameters.
if __name__ == "__main__":
    GLOBALS.buildControllerModel()
    plotGains()
