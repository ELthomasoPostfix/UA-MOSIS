from Diagrams.PIDController import PID
from pyCBD.scheduling import TopologicalScheduler
from pyCBD.depGraph import createDepGraph
from pyCBD.converters import CBDDraw

from pyCBD.Core import BaseBlock, Port

from typing import List
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


def CBD2FMU(model):
    depGraph = createDepGraph(model, 0)

    scheduler = TopologicalScheduler()
    sortedGraph = scheduler.obtain(depGraph, 1, 0.0)

    print(depGraph)
    print(sortedGraph)

    print("*"*100)


    model = model.flattened()
    depGraph = createDepGraph(model, 0)

    scheduler = TopologicalScheduler()
    sortedGraph = scheduler.obtain(depGraph, 1, 0.0)

    print(depGraph)
    print(sortedGraph)

    flattenedBlocks = [block for blocks in sortedGraph for block in blocks]
    ioPorts, portBlocks = [], []
    for block in flattenedBlocks:
        (ioPorts if isinstance(block, Port) else portBlocks).append(block)

    # SortedGraph consists of arrays of multiple blocks
    ports = [getPorts(portBlock) for portBlock in portBlocks]
    ports.insert(0, ioPorts)

    flattenedPorts = [port for ports in ports for port in ports]

    runJinjaTemplate("./sources/defs.h.jinja", {"ports": flattenedPorts, "getPortName": getPortName})
    runJinjaTemplate("./sources/eq0.c.jinja", {"blocks": flattenedBlocks, "getEquation": getEquation})
    runJinjaTemplate("./sources/eqs.c.jinja", {"blocks": flattenedBlocks, "getEquation": getEquation})
    runJinjaTemplate("./modelDescription.xml.jinja",
                     {"ports": flattenedPorts, "getConstantPort": getConstantPort, "getInitialPort": getInitialPort,
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
