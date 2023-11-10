import os
import csv
import numpy as np
from typing import List
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
from util import readMat, carCollided, GLOBALS


def plotGains() -> None:
    KpList = [0.001, 1, 20]
    KiList = [0.001, 1, 20]
    KdList = [0.001, 20, 40]

    # Create 3 x 9 subplots (with columns of 3 grouped)
    fig, ax = plt.subplots(3, 9, figsize=(100, 20))
    KpIdx, KiIdx, KdIdx = 0, 0, 0

    data = []

    # Plot every 3x3 combination of gains in a 3x3 subplot
    for Kp in KpList:
        KiIdx = 0
        for Ki in KiList:
            KdIdx = 0
            for Kd in KdList:
                timeData, leadCarDistanceData, plantCarDistanceData = run_simulation(
                    "controller",
                    {"Kp_start": Kp, "Ki_start": Ki, "Kd_start": Kd},
                    ["time", "lead_car.y", "Plant.y"]
                )

                collided, collision_idx = carCollided(leadCarDistanceData, plantCarDistanceData)

                column_idx = (KpIdx * 3) + KdIdx
                row_idx = KiIdx - 1

                data.append((column_idx, row_idx, timeData, leadCarDistanceData, plantCarDistanceData, collided, collision_idx))

                KdIdx += 1
            KiIdx += 1
        KpIdx += 1

    for (column_idx, row_idx, timeData, leadCarDistanceData, plantCarDistanceData, collided, collision_idx) in data:
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
            ax[row_idx][column_idx].text(timeData[collision_idx], 0, 'Collision', rotation=90, color='r')


    # Add legend to last subplot
    ax[2][8].legend().set_visible(True)

    fig.tight_layout()

    plt.show()


if __name__ == "__main__":
    GLOBALS.buildControllerModel()
    plotGains()
