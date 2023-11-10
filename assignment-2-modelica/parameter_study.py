import os
import csv
import numpy as np
from typing import List
from matplotlib import pyplot as plt
from scipy import io  # You need scipy package to read MAT-files
import seaborn as sns
import pandas as pd
from util import readMat, carCollided, run_simulation


def visualizePlant() -> None:
    timeData, displacementData, velocityData, accelerationData = run_simulation(
        "plant",
        {"A": 60, "b": 0.86, "M": 1500, "u": 0},
        ["time", "x", "v", "a"]
    )

    dragCoeff: float = 0.86

    dragForcesData: List[float] = [velocity ** 2 * dragCoeff for velocity in velocityData]

    # Visualize each type of data separately
    dataTypes = [
        # ("Displacement (m)", displacementData, "#2D6F8E"),
        ("Velocity (m/s)", velocityData, "#2AB07E"),
        ("Acceleration (m/s²)", accelerationData, "#D22B26"),
        ("Drag Force (N)", dragForcesData, "#FDB515")
    ]

    # Draw each data type separately
    # for dataType in dataTypes:
    #     sns.set_style("whitegrid")
    #     sns.lineplot(x=timeData, y=dataType[1], color=dataType[2])
    #
    #     plt.title(f"Plant Model: {dataType[0]} over Time")
    #     plt.xlabel("Time (s)")
    #     plt.ylabel(dataType[0])
    #     plt.tight_layout()
    #
    #     plt.show()

    # Combine the three data types into one plot, but with different y-axes series
    fig, ax1 = plt.subplots()
    curax = ax1
    for i, dataType in enumerate(dataTypes):
        curax.set_xlabel("Time (s)")
        if i == len(dataTypes) - 1:
            curax.spines["right"].set_position(("axes", 1.15))

        curax.set_ylabel(dataType[0], color=dataType[2])
        curax.plot(timeData, dataType[1], color=dataType[2])
        curax.tick_params(axis="y", labelcolor=dataType[2])
        if i != len(dataTypes) - 1:
            curax = ax1.twinx()

    plt.title("Plant Model: Displacement, Velocity, and Acceleration over Time")
    plt.tight_layout()

    plt.savefig("plant_model.png")

    plt.show()



if __name__ == "__main__":
    visualizePlant()
