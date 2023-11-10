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
from util import readMat, carCollided

def singleSimulation(Kp: float, Ki: float, Kd: float) -> [List[float], List[float], List[float]]:
    """Perform a single simulation using the model binary.

    :param Kp: The proportional gain
    :param Ki: The integral gain
    :param Kd: The derivative gain
    :return: (timestamp list, lead car distance list, plant car distance list)
    """
    packageName: str = "PCarController"
    modelName: str = "CarCruiseController"
    outputFilePath: str = f"{modelName}_res.mat"

    os.chdir(f"{packageName}.{modelName}")
    # OS-agnostic executable call
    # Executing the simulation ONLY works iff.
    #   1) the .bat file is called
    #   2) the call happens where the .bat file is located
    #   3) OMEdit is turned off (or at least does not have the model file opened?)
    # ==> This is windows specific, ubuntu users are on their own :(
    os.system(f".\{modelName}.bat -override Kp_start={Kp},Ki_start={Ki},Kd_start={Kd}")

    # Obtain the variable values by reading the MAT-file
    names, data = readMat(outputFilePath)
    os.chdir("..")  # Reset dir for next calls

    timeData: List[float] = data[names.index("time")]
    leadCarDistanceData: List[float] = data[names.index("lead_car.y")]
    plantCarDistanceData: List[float] = data[names.index("Plant.y")]

    return timeData, leadCarDistanceData, plantCarDistanceData

def rootMeanSquaredError(observedData: List[float], predictedData: List[float]) -> float:
    """Compute the root mean squared error for the given two same-sized lists.
        MSE = sqrt(summ_i (( observedData[i] - predictedData[i] )**2) / (1 / n))

    :param observedData: The data that is subtracted from in the summation
    :param predictedData: The data that is subtracted with in the summation
    :return: The MSE
    """
    assert len(observedData) == len(
        predictedData), f"Can only compute RMSE for same-sized lists: got {len(observedData)} != {len(predictedData)}"
    rmse: float = 0
    for idx in range(0, len(observedData)):
        rmse += pow(observedData[idx] - predictedData[idx], 2) / len(observedData)
    return np.sqrt(rmse)



def optimizeGains() -> None:
    collidedList: List[bool] = []
    rmseList: List[float] = []
    gainList: List[(int, int, int)] = []

    for Kp in np.arange(210, 400, 10):
        for Ki in np.arange(1, 21, 1):
            for Kd in np.arange(1, 21, 1):
                timeData, leadCarDistanceData, plantCarDistanceData = singleSimulation(Kp, Ki, Kd)

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
    df = pd.DataFrame({'Kp': [gain[0] for gain in gainList], 'Ki': [gain[1] for gain in gainList], 'Kd': [gain[2] for gain in gainList], 'RMSE': rmseList})
    df.to_csv("gain_data.csv")


# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop ove the combinations of parameters.
if __name__ == "__main__":
    optimizeGains()
