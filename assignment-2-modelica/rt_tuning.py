import os
import numpy as np
from typing import List
from util import readMat, carCollided


def singleSimulation(rt: float, Kp: float, Ki: float, Kd: float) -> [List[float], List[float], List[float]]:
    """Perform a single simulation using the model binary.

    :param rt: The chosen target inter-vehicle distance
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
    os.system(f".\{modelName}.bat -override rt_start={rt},Kp_start={Kp},Ki_start={Ki},Kd_start={Kd}")

    # Obtain the variable values by reading the MAT-file
    names, data = readMat(outputFilePath)
    os.chdir("..")  # Reset dir for next calls

    timeData: List[float] = data[names.index("time")]
    leadCarDistanceData: List[float] = data[names.index("lead_car.y")]
    plantCarDistanceData: List[float] = data[names.index("Plant.y")]

    return timeData, leadCarDistanceData, plantCarDistanceData

def optimizeMinVehicleSpacing() -> None:
    Kp: float = 390
    Ki: float = 20
    Kd: float = 20
    rtList: List[float] = []
    rtCollidedList: List[float] = []

    for rt in np.arange(9.9, 0, -0.1):
        timeData, leadCarDistanceData, plantCarDistanceData = singleSimulation(
            rt=rt,
            Kp=Kp,
            Ki=Ki,
            Kd=Kd)

        # Manually fix duplicate final simulation value
        timeData = timeData[:len(timeData) - 1]
        leadCarDistanceData = leadCarDistanceData[:len(leadCarDistanceData) - 1]
        plantCarDistanceData = plantCarDistanceData[:len(plantCarDistanceData) - 1]

        collided, collision_idx = carCollided(leadCarDistanceData, plantCarDistanceData)
        leadCarDistanceData = [dist - 10 for dist in leadCarDistanceData]

        rtList.append(rt)
        if collided: rtCollidedList.append(rt)

    rtEarliestCollisionIdx: int = rtList.index(rtCollidedList[0]) if len(rtCollidedList) > 0 else None
    rtEarliestCollision: float = rtList[rtEarliestCollisionIdx]
    rtLatestSafe: float = rtList[rtEarliestCollisionIdx - 1] if rtEarliestCollisionIdx > 0 else None

    print("Earliest Collision: ", rtEarliestCollision)
    print("Latest Safe:        ", rtLatestSafe)


# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop ove the combinations of parameters.
if __name__ == "__main__":
    optimizeMinVehicleSpacing()