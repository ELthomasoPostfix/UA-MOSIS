import os
import numpy as np
from typing import List, Tuple
from util import readMat, carCollided, GLOBALS, run_simulation, plotTrace
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt


def optimizeMinVehicleSpacing() -> tuple[float, float]:
    Kp: float = 390
    Ki: float = 20
    Kd: float = 20
    rtList: List[float] = list(np.arange(9.9, 0, -0.1))
    rtCollidedList: List[float] = []
    rtCollisionIndexList: List[int] = []

    for rt in rtList:
        timeData, leadCarDistanceData, plantCarDistanceData = run_simulation(
            "controller",
            {"rt_start": rt, "Kp_start": Kp, "Ki_start": Ki, "Kd_start": Kd},
            ["time", "lead_car.y", "Plant.y"]
        )


        # Manually fix duplicate final simulation value
        timeData = timeData[:len(timeData) - 1]

        leadCarDistanceData = leadCarDistanceData[:len(leadCarDistanceData) - 1]
        plantCarDistanceData = plantCarDistanceData[:len(plantCarDistanceData) - 1]

        collided, collision_idx = carCollided(leadCarDistanceData, plantCarDistanceData)
        leadCarDistanceData = [dist - 10 for dist in leadCarDistanceData]

        rtCollidedList.append(collided)
        rtCollisionIndexList.append(collision_idx)

    timeLength = timeData.max()

    # Find first collision
    rtEarliestCollisionIdx: int = rtCollidedList.index(True)

    rtEarliestCollision = timeLength
    if rtEarliestCollisionIdx == -1:
        print('No collision found')
    else:
        rtEarliestCollision: float = rtList[rtEarliestCollisionIdx]
        rtLatestSafe: float = rtList[rtEarliestCollisionIdx - 1]

        print("Earliest Collision: ", rtEarliestCollision)
        print("Latest Safe:        ", rtLatestSafe)

    sns.set_style(style="whitegrid")
    rtCollisionIndexList = [timeLength if x == -1 else x for x in rtCollisionIndexList]
    hasCollided = [x != timeLength for x in rtCollisionIndexList]

    # Plot barplot with values going from high to low
    df = pd.DataFrame({'rt': rtList, 'collision': rtCollisionIndexList, 'hasCollided': hasCollided})
    df = df.sort_values(by='rt', ascending=False)

    colorSet = ['green', 'red']

    sns.barplot(x='rt', y='collision', data=df, hue='hasCollided', palette=colorSet, errorbar=None, width=1)
    plt.xlabel('r(t) = Target Inter-Vehicle Distance (m)')
    plt.ylabel('t = Time of Collision (s)')

    # Only show x-axis labels for every 5th value, rounded to 1 decimal
    plt.xticks(np.arange(0, len(rtList), 5), [round(x - 0.4, 1) for x in rtList[::5]][::-1])

    # Set legend labels
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles, ['Safe', 'Collision'], title='Collision Status')

    plt.gca().invert_xaxis()

    plt.savefig('rt_collision.png')
    plt.show()

    return rtLatestSafe, rtEarliestCollision


if __name__ == "__main__":
    GLOBALS.buildControllerModel()
    rtLatestSafe, rtEarliestCollision = optimizeMinVehicleSpacing()

    plotTrace(rt=rtLatestSafe, Kp=390, Ki=20, Kd=20)
    plotTrace(rt=rtEarliestCollision, Kp=390, Ki=20, Kd=20)



