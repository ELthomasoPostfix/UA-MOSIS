# This file contains example Python code to demonstrate the simulation of the newtonCooling Modelica model
# You need os package to execute commands in shell
import os
import csv
import numpy as np
from typing import List
from matplotlib import pyplot as plt
from scipy import io  # You need scipy package to read MAT-files
import seaborn as sns
import pandas as pd
from util import readMat, carCollided, rootMeanSquaredError, GLOBALS, run_simulation


def optimizeGains() -> None:
    collidedList: List[bool] = []
    rmseList: List[float] = []
    gainList: List[(int, int, int)] = []

    for Kp in np.arange(210, 400, 10):
        for Ki in np.arange(1, 21, 1):
            for Kd in np.arange(1, 21, 1):
                timeData, leadCarDistanceData, plantCarDistanceData = run_simulation(
                    "controller",
                    {"Kp_start": Kp, "Ki_start": Ki, "Kd_start": Kd},
                    ["time", "lead_car.y", "Plant.y"]
                )

                # Manually fix duplicate final simulation value
                timeData = timeData[:len(timeData) - 1]
                leadCarDistanceData = leadCarDistanceData[:len(leadCarDistanceData) - 1]
                plantCarDistanceData = plantCarDistanceData[:len(plantCarDistanceData) - 1]

                collided, collision_idx = carCollided(leadCarDistanceData, plantCarDistanceData)
                leadCarDistanceData = [dist - 10 for dist in leadCarDistanceData]

                collidedList.append(collided)
                rmseList.append(rootMeanSquaredError(leadCarDistanceData, plantCarDistanceData))
                gainList.append((Kp, Ki, Kd))

    # Select min RMSE that did not collide
    rmseList = [rmseList[i] for i in range(len(rmseList)) if not collidedList[i]]
    gainList = [gainList[i] for i in range(len(gainList)) if not collidedList[i]]

    minRMSE: float = min(rmseList)
    minRMSEIndex: int = rmseList.index(minRMSE)
    minRMSEBvalue: (int, int, int) = gainList[minRMSEIndex]
    gainListIndex = [i for i in range(len(gainList))]

    print("min rmse ", minRMSE)
    print("min rmse idx ", minRMSEIndex)
    print("min rmse gain tuple ", minRMSEBvalue)

    # sns.set_style("whitegrid")
    # sns.scatterplot(x=gainListIndex, y=rmseList, hue=collidedList, palette=["green", "red"], legend="full")
    #
    # # Plot the plot
    # plt.xlabel("Gain tuple index")
    # plt.ylabel("RMSE")
    # plt.show()

    # Create 3D scatterplot with Kp, Ki, Kd on axes and RMSE as color using seaborn
    # sns.set_style("whitegrid")

    # Create a dataframe with the data
    df = pd.DataFrame({'Kp': [gain[0] for gain in gainList], 'Ki': [gain[1] for gain in gainList], 'Kd': [gain[2] for gain in gainList], 'RMSE': rmseList, 'Collided': collidedList})
    df.to_csv("gain_data.csv")


# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop ove the combinations of parameters.
if __name__ == "__main__":
    GLOBALS.buildControllerModel()
    optimizeGains()
