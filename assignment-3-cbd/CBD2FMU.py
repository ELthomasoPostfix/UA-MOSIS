from Diagrams.PIDController import PID
from pyCBD.scheduling import TopologicalScheduler
from pyCBD.depGraph import createDepGraph
from pyCBD.converters import CBDDraw

from pyCBD.Core import CBD, BaseBlock, Port

from typing import List, Mapping
from jinja2 import Template, Environment, FileSystemLoader
from enum import IntEnum
import zipfile
import os

from pathlib import Path

INPUT_DIR = "./template-fmu"
OUTPUT_DIR = "./output-fmu"


class Iteration(IntEnum):
    """
	Specifies which iteration the equation should solve for.
	"""

    INITIAL = 0
    """The initial iteration."""

    CONTINUOUS = 1
    """The continuous iteration."""


def runJinjaTemplate(template: str, args: dict):
    templateLoader = FileSystemLoader(searchpath=INPUT_DIR)
    templateEnv = Environment(loader=templateLoader)
    templatePath = Path(template)
    template = templateEnv.get_template(template)

    output = template.render(args)

    with open(Path(OUTPUT_DIR) / templatePath.with_suffix(""), "w") as outFile:
        outFile.write(output)


def getPortName(port: Port, dot=False):
    portname = f"{port.getPath('.')}"
    return portname.replace(".", "_") if not dot else portname


def getEquation(block: BaseBlock, iteration: Iteration):
    # TODO: in case of no flattening, have to recursively call getEquation so that a set of equations (as a string) is returned in the end???
    outputString = ""

    if isinstance(block, Port):
        block: Port
        if block.direction == 0:
            outputString = "\n".join(
                [f"{getPortName(conn.target)} = {getPortName(block)};" for conn in block.getOutgoing()])
        else:
            outputString = f"{getPortName(block)} = {getPortName(block.getIncoming().source)};"
    else:
        inputs: List[Port] = block.getInputPorts()
        outputs: List[Port] = block.getOutputPorts()
        blockType = block.getBlockType()[:-5]

        if blockType != "Delay":
            for input in inputs:
                outputString += f"{getPortName(input)} = {getPortName(input.getIncoming().source)};\n"

        match blockType:
            case "Constant":
                outputString += f"{getPortName(outputs[0])} = {block.getValue()};"
            case "Adder":
                outputString += f"{getPortName(outputs[0])} = {getPortName(inputs[0])} + {getPortName(inputs[1])};"
            case "Product":
                outputString += f"{getPortName(outputs[0])} = {getPortName(inputs[0])} * {getPortName(inputs[1])};"
            case "Negator":
                outputString += f"{getPortName(outputs[0])} = -{getPortName(inputs[0])};"
            case "Inverter":
                outputString += f"{getPortName(outputs[0])} = 1 / {getPortName(inputs[0])};"
            case "DeltaT":
                outputString += f"{getPortName(outputs[0])} = delta;"
            case "Delay":
                outputString += f"{getPortName(inputs[0])} = {getPortName(inputs[0].getIncoming().source)};\n"
                # Only set the IC value if it is the initial iteration, otherwise it is considered as the delay variable
                if iteration == Iteration.INITIAL.value:
                    outputString += f"{getPortName(inputs[1])} = {getPortName(inputs[1].getIncoming().source)};\n"

                # Does not introduce any additional variables, IC is considered as the delay variable after assigning it to the output
                outputString += f"{getPortName(outputs[0])} = {getPortName(inputs[1])};\n"
                outputString += f"{getPortName(inputs[1])} = {getPortName(inputs[0])};"
            case _:
                print("ERR:", block.getBlockType())

    return outputString


def getPorts(block: BaseBlock):
    # match block.getBlockType()[:-5]:
    #     case "Delay":
    #         delayPort = Port("DELAY", 0, block)
    #         return block.getInputPorts() + [delayPort] + block.getOutputPorts()
    #     case _:
    return block.getInputPorts() + block.getOutputPorts()


def isKnownValuePort(port: Port):
    return port.block.getBlockType()[:-5] == "Constant"


def getConstantPort(port: Port):
    return "constant" if isKnownValuePort(port) else "continuous"


def getInitialPort(port: Port):
    return "exact" if isKnownValuePort(port) or (not port.getIncoming() and port.direction == 0) else "calculated"


def getPortCausality(port: Port):
    if port.direction == 0 and not port.getIncoming():
        return "input"
    elif port.direction == 1 and not port.getOutgoing():
        return "output"
    else:
        return "local"


def hasStartValue(port: Port):
    if isKnownValuePort(port):
        return f'start="{port.block.getValue()}"'
    elif not port.getIncoming() and port.direction == 0:
        return 'start="0"'
    else:
        return ""

def generateTopoSchedule(flattenedModel: CBD, iteration: int):
    """Create a topoligically sorted cumputation schedule for the
     given flattened CBD model.
    
    :param flattenedModel: The CBD model to derive the schedule from
    :param iteration: The iteration to create a schedule for
    :return: The schedule as a list of BaseBlock and Port objects
    """
    depGraph = createDepGraph(flattenedModel, iteration, ignore_hierarchy=True)
    print(depGraph, "\n"*3) # TODO delete
    scheduler = TopologicalScheduler()
    topoSchedule = scheduler.obtain(depGraph, iteration, 0.0)
    topoSchedule = [
        block
        for strongcomponent in topoSchedule
            for block in strongcomponent
    ]
    for v in topoSchedule:
        print(v) # TODO delete

    # TODO: depgraph and schedule prints
    # print(depGraph)
    # print("\n"*6)
    # for b in topoSchedule:
    #     print(b)

    return topoSchedule


def extractFlattenedPorts(topoSchedule) -> List[Port]:
    """Extract a flattened list of ports from a topological computation schedule.

    :param topoSchedule: The topological schedule to transform
    :return: The flattened list of Port objects
    """
    ioPorts, portBlocks = [], []
    for block in topoSchedule:
        (ioPorts if isinstance(block, Port) else portBlocks).append(block)

    # SortedGraph consists of arrays of multiple blocks
    ports = [getPorts(portBlock) for portBlock in portBlocks]
    ports.insert(0, ioPorts)

    flattenedPorts = [port for ports in ports for port in ports]
    return flattenedPorts


def CBD2FMU(model: CBD):
    # TODO: Flattening fixes TopologicalScheduler issues
    # model = model.flattened()

    topoSchedule0 = generateTopoSchedule(flattenedModel=model, iteration=0)
    runJinjaTemplate("./sources/eq0.c.jinja", {"blocks": topoSchedule0, "getEquation": getEquation})
    flattenedPorts0 = extractFlattenedPorts(topoSchedule0)

    topoSchedule = generateTopoSchedule(flattenedModel=model, iteration=1)
    runJinjaTemplate("./sources/eqs.c.jinja", {"blocks": topoSchedule, "getEquation": getEquation})
    flattenedPorts = extractFlattenedPorts(topoSchedule)

    # A set for faster membership checking to merge both lists while maintaining the original port order
    fp0 = set(flattenedPorts0)
    flattenedPortsCombined = flattenedPorts0 + [fport for fport in flattenedPorts if fport not in fp0]

    runJinjaTemplate("./sources/defs.h.jinja", {"ports": flattenedPortsCombined, "getPortName": getPortName})
    runJinjaTemplate("./modelDescription.xml.jinja",
                     {"ports": flattenedPortsCombined, "getConstantPort": getConstantPort, "getInitialPort": getInitialPort,
                      "hasStartValue": hasStartValue, "getPortCausality": getPortCausality, "getPortName": getPortName})


def zipFMU(directory, file_name):
    # Zip together all files in ./output-fmu to PID.fmu
    zipf = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)

    # Walk over directory contents except for the directory itself
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Prevent the root directory from being included in the zip
            zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), directory))

    zipf.close()


if __name__ == "__main__":
    cbd = PID("PID")
    CBD2FMU(cbd)
    zipFMU(OUTPUT_DIR, "PID.fmu")
