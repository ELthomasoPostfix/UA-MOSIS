# This file contains example Python code to demonstrate the simulation of the newtonCooling Modelica model
# You need os package to execute commands in shell
import os
import csv
import numpy as np
from typing import List
from matplotlib import pyplot
from scipy import io    # You need scipy package to read MAT-files
from util import readMat

def singleSimulation(A: float, b: float, M: float, u: float) -> None:
    """Perform a single simulation using the model binary.

    :param A: The forward gain (N/V) from the control signal
    :param M: The total mass (kg) of the plant
    :param b: The plant's drag coefficient(kg/m)
    :param u: The control signal (V)
    :return: (timestamp list, displacement data list)
    """
    # TODO CHANGE TO "PCarCruiseController"
    packageName: str = "CarCruiseController"
    modelName: str   = "PlantModel"
    outputFilePath: str  = f"{modelName}_res.mat"
    
    os.chdir(f"{packageName}.{modelName}")
    # OS-agnostic executable call
    # Executing the simulation ONLY works iff.
    #   1) the .bat file is called
    #   2) the call happens where the .bat file is located
    #   3) OMEdit is turned off (or at least does not have the model file opened?)
    # ==> This is windows specific, ubuntu users are on their own :(
    os.system(f".\{modelName}.bat -override A={A},M={M},b={b},u={u}")

    # Obtain the variable values by reading the MAT-file
    names, data = readMat(outputFilePath)
    os.chdir("..")  # Reset dir for next calls

    timeData: List[float] = data[names.index("time")]
    displacementData: List[float] = data[names.index("x")]

    return timeData, displacementData

def meanSquaredError(observedData: List[float], predictedData: List[float]) -> float:
    """Compute the mean squared error for the given two same-sized lists.
        MSE = (1 / n) * summ_i ( observedData[i] - predictedData[i] )**2

    :param observedData: The data that is subtracted from in the summation
    :param predictedData: The data that is subtracted with in the summation
    :return: The MSE
    """
    assert len(observedData) == len(predictedData), f"Can only compute MSE for same-sized lists: got {len(observedData)} != {len(predictedData)}"
    mse: float = 0
    for idx in range(0, len(observedData)):
        mse += pow(observedData[idx] - predictedData[idx], 2)
    return mse / len(observedData)


def optimizeDrag() -> None:
    # Load comparison data
    refDisplacementData: List[float] = []
    with open("./assignment-files/deceleration_data.csv", "r") as referenceFile:
        reader = csv.reader(referenceFile)
        next(reader)    # Skip header
        refDisplacementData = [float(line[1]) for line in reader]

    # b in (0.00, 3.00]
    bRange = [bv for bv in np.arange(3.00, 0.00, -0.01)]
    mseList: List[float] = []
    for bValue in bRange:
        timeData, displacementData = singleSimulation(A=60, b=bValue, M=1500, u=0)

        # Manually fix duplicate final simulation value
        timeData = timeData[:len(timeData) - 1]
        displacementData = displacementData[:len(displacementData) - 1]

        mseList.append(meanSquaredError(refDisplacementData, displacementData))

    # mseList = [val - min(mseList) for val in mseList]

    # bRange is xvalues, mseList is yvalues find fitting function
    # degrees = 4
    # deg = np.polyfit(bRange, mseList, degrees)
    # # Print as string
    # stre = " + ".join([f"{deg[i]}*x**{degrees - i}" for i in range(degrees + 1)])
    # print(stre)

    minMSE: float = min(mseList)
    minMSEIndex: int = mseList.index(minMSE)
    minMSEBvalue: float = bRange[minMSEIndex]
    print("min mse ", minMSE)
    print("min mse idx ", minMSEIndex)
    print("min mse b-value ", minMSEBvalue)


    openDataPlot(bRange, mseList,'b (kg/m)','MSE')


# This function plots the data from the simulation.
# xdata is x-axis data
# ydata is corresponding y-axis data
# xLabel is the string label value to be displayed in the plot for the x axis
# yLabel is the string label value to be displayed in the plot for the y axis
def openDataPlot(xdata, ydata, xLabel, yLabel):
    figure, axis = pyplot.subplots()
    axis.plot(xdata, ydata)
    pyplot.xlabel(xLabel)
    pyplot.ylabel(yLabel)
    pyplot.show()

# "function" that calls the single simulation function from shell. In your code, this function call should be in a loop ove the combinations of parameters.
if __name__ == "__main__":
    optimizeDrag()

# The follwing function is an alternative way of executing/simulating the Modelica model using the OMPython package. This method is not recommended.
# from OMPython import OMCSessionZMQ, ModelicaSystem
# def singleSimulationOMPython(T_inf=298.15, T0=363.15, h=0.7, A=1.0, m=0.1, c_p=1.2):
#     omc = OMCSessionZMQ()
#     model = ModelicaSystem('example.mo','NewtonCoolingWithTypes')
#     model.buildModel('T')
#     print('Performing simulation: Ambient Temp.:',str(T_inf),
#                                ', Initial Temp.:',str(initTemp),
#                                ', Convection Coeff.:',str(h),
#                                ', Area:',str(A),
#                                ', Mass:',str(m),
#                                ', Specific Heat:',str(Cp))
#
#     model.setSimulationOptions(["stepSize=0.01",
#                                 "tolerance=1e-9",
#                                 "startTime=0",
#                                 "stopTime=10"])
#     model.setParameters(['T_inf='+str(T_inf),
#                          'T0='+str(T0),
#                          'h='+str(h),
#                          'A='+str(A),
#                          'm='+str(m),
#                          'c_p='+str(c_p)])
#     model.simulate()
#     samples = model.getSolutions(["time", "T"])
#     openDataPlot([samples[0]],[samples[1]],'time (seconds)','temperature (C)')
