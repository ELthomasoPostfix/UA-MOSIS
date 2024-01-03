from pypdevs.DEVS import Port
from itertools import chain

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


def tuple_avg(tuple_list: list[tuple]) -> tuple:
    """
    Recursively calculate the average of all the values in the given list of tuples.
    :param tuple_list: A list of tuples.
    :return: A tuple with the same length as the given tuples, but with the average values.
    """
    return tuple(sum(t) / len(t) for t in zip(*tuple_list))


def dict_avg(dict_list: list[dict]) -> dict:
    """
    Recursively calculate the average of all the values in the given list of dictionaries.
    :param dict_list: A list of dictionaries.
    :return: A dictionary with the same keys as the given dictionaries, but with the average values.
    """
    result = {}
    for key in dict_list[0].keys():
        # If value is str, skip
        if isinstance(dict_list[0][key], str):
            continue
        elif isinstance(dict_list[0][key], list):
            if isinstance(dict_list[0][key][0], dict):
                result[key] = dict_avg(list(chain.from_iterable(d[key] for d in dict_list)))
            elif isinstance(dict_list[0][key][0], tuple):
                result[key] = tuple_avg(list(chain.from_iterable(d[key] for d in dict_list)))
        else:
            result[key] = sum(d[key] for d in dict_list) / len(dict_list)
    return result
