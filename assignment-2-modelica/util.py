import os, glob, OMPython
import numpy as np
from scipy import io  # You need scipy package to read MAT-files
from typing import List

from matplotlib import pyplot as plt

# Reuse this exact function to read MAT-file data.
# matFileName is the name of the MAT-file generated on execution of a Modelica executable
# The output is [names, data] where names is an array of strings which are names of variables, data is an array of values of the associated variable in the same order
def readMat(matFileName):
    dataMat = io.loadmat(matFileName)
    names = [''] * len(dataMat['name'][0])
    data = [None] * len(names)
    # Check if the matrix of metadatas are transposed.
    if dataMat['Aclass'][3] == 'binTrans':
        # If the matrix of  matadata needs to be transposed, the names nead to be read from each string
        for x in range(len(dataMat['name'])):
            for i in range(len(dataMat['name'][x])):
                if dataMat['name'][x][i] != '\x00':
                    names[i] = names[i] + dataMat['name'][x][i]
        # If the matrix of metadata needs to be transposed, the index of variable trace needs to be read in a transposed fashion
        for i in range(len(names)):
            # If it is a variable, read the whole array
            if (dataMat['dataInfo'][0][i] == 0) or (dataMat['dataInfo'][0][i] == 2):
                data[i] = dataMat['data_2'][dataMat['dataInfo'][1][i] - 1]
            # If it is a parameter, read only the first value
            elif dataMat['dataInfo'][0][i] == 1:
                data[i] = dataMat['data_1'][dataMat['dataInfo'][1][i] - 1][0]
    else:
        # If the matrix of metadata need not be transposed, the names can be read directly as individual strings
        names = dataMat['name']
        # If the matrix of metadata need not be transposed, the index of variable trace needs to be read directly
        for i in range(len(names)):
            # If it is a variable, read the whole array
            if (dataMat['dataInfo'][i][0] == 0) or (dataMat['dataInfo'][i][0] == 2):
                data[i] = dataMat['data_2'][dataMat['dataInfo'][i][1] - 1]
            # If it is a parameter, read only the first value
            elif dataMat['dataInfo'][i][0] == 1:
                data[i] = dataMat['data_1'][dataMat['dataInfo'][i][1] - 1][0]
    # Return the names of variables, and their corresponding values
    return [names, data]


def carCollided(leadCarDistanceData: List[float], plantCarDistanceData: List[float]) -> bool:
    for idx in range(0, len(leadCarDistanceData)):
        if plantCarDistanceData[idx] >= leadCarDistanceData[idx]:
            return True, idx
    return False, -1


def meanSquaredError(observedData: List[float], predictedData: List[float]) -> float:
    """Compute the mean squared error for the given two same-sized lists.
        MSE = (1 / n) * summ_i ( observedData[i] - predictedData[i] )**2

    :param observedData: The data that is subtracted from in the summation
    :param predictedData: The data that is subtracted with in the summation
    :return: The MSE
    """
    assert len(observedData) == len(
        predictedData), f"Can only compute MSE for same-sized lists: got {len(observedData)} != {len(predictedData)}"
    mse: float = 0
    for idx in range(0, len(observedData)):
        mse += pow(observedData[idx] - predictedData[idx], 2)
    return mse / len(observedData)


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


# A link to the OMPython package docs: https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/ompython.html#ompython
# A link to the OpenModelica scripting docs: https://build.openmodelica.org/Documentation/OpenModelica.Scripting.html
def buildModel(modelFilePath: str, modelName: str, packageName: str, dependencies: List[str]):
    """Build the given model. All paths must be relative.
    Janky method, do not trust it too much.
    
    """

    # All file paths will need to relatively be accessed one level higher
    combinedName: str = f"{packageName}.{modelName}"
    targetBinName: str = f"{modelName}.bat"

    print()
    print(f"Build from model file at {modelFilePath}")
    print()
    print("-- MODEL BUILD INFO --")
    print(f"model name:   ", modelName)
    print(f"package name: ", packageName)
    print(f"dst dir name: ", combinedName)
    print(f"dependencies: ", dependencies)
    print()
    print()

    modelFilePath = f"../{modelFilePath}"
    for idx, dependency in enumerate(dependencies):
        if '.mo' in dependency:
            dependencies[idx] = f"../{dependency}"

    # Setup
    if not os.path.exists(combinedName):
        os.mkdir(combinedName)
    os.chdir(combinedName)

    # DONT INITIALIZE YET PLS I JUST WANT TO EDIT SIMULATION PARAMS AND NOT HAVE TO COMPILE TWICE BECAUSE WHY TF WOULD I
    def doNotBuildModel(self=None):
        return

    buildFunction = OMPython.ModelicaSystem.buildModel
    OMPython.ModelicaSystem.buildModel = doNotBuildModel

    # Setup model
    model = OMPython.ModelicaSystem(modelFilePath, combinedName, dependencies)
    # HAVE YOUR STUPID BUILD FUNCTION BACK
    OMPython.ModelicaSystem.buildModel = buildFunction
    model.buildModel()

    # Cleanup
    for f in glob.glob("*.[och]"):
        os.remove(f)
    if os.path.exists(targetBinName):
        os.remove(targetBinName)
    os.rename(f"{combinedName}.bat", targetBinName)
    os.chdir("..")


def run_simulation(type: "plant" or "controller", input_param: dict, output_param: List[str]):
    """Perform a single simulation using the model binary.

    :param type: The type of model to run, either "plant" or "controller"
    :param input_param: The arguments to pass to the model
    :param output_param: The arguments to read from the model
    """

    modelName: str = GLOBALS.controllerModelName if type == "controller" else GLOBALS.plantModelName
    packageName: str = GLOBALS.packageName
    outputFileName: str = GLOBALS.outputFileName(modelName)

    os.chdir(GLOBALS.outputDirName(packageName, modelName))

    # OS-agnostic executable call
    # Executing the simulation ONLY works iff.
    #   1) the .bat file is called
    #   2) the call happens where the .bat file is located
    #   3) OMEdit is turned off (or at least does not have the model file opened?)
    # ==> This is windows specific, ubuntu users are on their own :(
    command = f".\{modelName}.bat"
    if input_param:
        command += " -override " + ",".join([f"{key}={value}" for key, value in input_param.items()])
    print(command)
    os.system(f"{command} -r {outputFileName}")

    # Obtain the variable values by reading the MAT-file
    names, data = readMat(outputFileName)
    os.chdir("..")  # Reset dir for next calls

    return [data[names.index(param)] for param in output_param]


def plotTrace(rt=10, Kp=1, Ki=1, Kd=20) -> None:
    timeData, leadCarDistanceData, plantCarDistanceData, errorTermData, controlData = run_simulation(
        "controller",
        {"Kp_start": Kp, "Ki_start": Ki, "Kd_start": Kd, "rt_start": rt},
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

    ax.set_title(f"Kp={Kp}, Ki={Ki}, Kd={Kd}, rt={round(rt, 2)}")
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

    plt.savefig(f"line-plot-{Kp}-{Ki}-{Kd}-{round(rt, 2)}.png")
    plt.show()


class GLOBALS:
    packageName: str = "PCarController"

    plantModelName: str = "PlantModel"
    plantDependencies: List[str] = ["Modelica"]

    controllerModelName: str = "CarCruiseController"
    controllerDependencies: List[str] = ["Modelica", "./assignment-files/car_package.mo"]

    @staticmethod
    def outputDirName(packageName: str, modelName: str):
        return f"{packageName}.{modelName}"

    @staticmethod
    def outputFileName(modelName: str):
        return f"{modelName}_res.mat"

    @staticmethod
    def buildPlantModel():
        buildModel(f"./{GLOBALS.packageName}.mo", GLOBALS.plantModelName, GLOBALS.packageName,
                   GLOBALS.plantDependencies)

    @staticmethod
    def buildControllerModel():
        buildModel(f"./{GLOBALS.packageName}.mo", GLOBALS.controllerModelName, GLOBALS.packageName,
                   GLOBALS.controllerDependencies)
