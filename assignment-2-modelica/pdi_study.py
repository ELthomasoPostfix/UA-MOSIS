import os
import csv
import numpy as np
from typing import List
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
from util import readMat, carCollided, GLOBALS, run_simulation



def plotTrace(Kp, Ki, Kd) -> None:
    timeData, leadCarDistanceData, plantCarDistanceData, errorTermData, controlData = run_simulation(
        "controller",
        {"Kp_start": Kp, "Ki_start": Ki, "Kd_start": Kd},
        ["time", "lead_car.y", "Plant.y", "PID.et", "PID.ut"]
    )
    collided, collision_idx = carCollided(leadCarDistanceData, plantCarDistanceData)

    # Plot all data on a single graph
    fig, ax = plt.subplots()
    ax.plot(timeData, leadCarDistanceData, label='lead_car.y')
    ax.plot(timeData, plantCarDistanceData, label='plant_car.y')

    # Second y-axis
    ax2 = ax.twinx()
    # Dotted line for error term
    ax2.plot(timeData, errorTermData, label='PID.et', linestyle=':',color="#F6B28C")
    ax2.plot(timeData, controlData, label='PID.ut', linestyle=':', color="#2AB07E")

    ax.set_title(f"Kp={Kp}, Ki={Ki}, Kd={Kd}")
    ax.set_xlabel('time (seconds)')
    ax.set_ylabel('distance (meters)')

    handles, labels = ax.get_legend_handles_labels()
    labels[0] = 'Lead Car Distance'
    labels[1] = 'Plant Car Distance'
    ax.legend(handles, labels, loc='upper left')


    ax2.set_ylabel('error term / control effort')

    handles, labels = ax2.get_legend_handles_labels()
    labels[0] = 'Error Term'
    labels[1] = 'Control Effort'
    ax2.legend(handles, labels, loc='upper right')

    # Color the negative values in ax2 ticks red
    for tick in ax2.get_yticklabels():
        if not tick.get_text()[0].isdigit():
            tick.set_color('r')

    # Add collision indicator to graph
    if collided:
        ax.axvline(x=timeData[collision_idx], color='r', linestyle='--')
        ax.text(timeData[collision_idx], 0, 'Collision', rotation=90, color='r')

    plt.savefig(f"line-plot-{Kp}-{Ki}-{Kd}.png")
    plt.show()

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

                data.append((column_idx, row_idx, timeData, leadCarDistanceData, plantCarDistanceData, collided, collision_idx, Kp, Ki, Kd))

                KdIdx += 1
            KiIdx += 1
        KpIdx += 1

    for (column_idx, row_idx, timeData, leadCarDistanceData, plantCarDistanceData, collided, collision_idx, Kp, Ki, Kd) in data:
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

    plt.savefig("line-plot-overview.png")

    plt.show()


if __name__ == "__main__":
    GLOBALS.buildControllerModel()
    plotTrace(1, 1, 20)
    plotTrace(390, 20, 20)
    plotGains()
