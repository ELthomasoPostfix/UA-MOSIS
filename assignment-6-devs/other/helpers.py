from pypdevs.DEVS import Port

def getFullPortName(port: Port):
    parentName = ""
    currentParent = port.host_DEVS
    while currentParent is not None:
        parentName = currentParent.name + "." + parentName
        currentParent = currentParent.parent
    return parentName + port.name


def getOutgoingConnections(port: Port):
    for connection in port.inline:
        print(f"{getFullPortName(connection)} -> {getFullPortName(port)}")


def getIncomingConnections(port: Port):
    for connection in port.outline:
        print(f"{getFullPortName(port)} -> {getFullPortName(connection)}")