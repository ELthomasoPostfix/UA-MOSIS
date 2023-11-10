import os, glob, OMPython
from scipy import io  # You need scipy package to read MAT-files
from typing import List


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
    def doNotBuildModel(self=None): return
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
    def outputFilePath(packageName: str, modelName: str): 
        return f"{packageName}.{modelName}_res.mat"

    @staticmethod
    def buildPlantModel():
        buildModel(f"./{GLOBALS.packageName}.mo", GLOBALS.plantModelName, GLOBALS.packageName, GLOBALS.plantDependencies)

    @staticmethod
    def buildControllerModel():
        buildModel(f"./{GLOBALS.packageName}.mo", GLOBALS.controllerModelName, GLOBALS.packageName, GLOBALS.controllerDependencies)
