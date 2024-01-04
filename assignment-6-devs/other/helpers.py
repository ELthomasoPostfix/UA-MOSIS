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


def avg(list_: list) -> float:
    """
    Recursively calculate the average of all the values in the given list.
    :param list_: A list of values.
    :return: The average of the given values.
    """
    if isinstance(list_[0], str):
        return list_[0]
    return sum(list_) / len(list_)


def std(list_: list) -> float | None:
    """
    Recursively calculate the standard deviation of all the values in the given list.
    :param list_: A list of values.
    :return: The standard deviation of the given values.
    """
    if isinstance(list_[0], str):
        return None
    avg_ = avg(list_)
    return (sum((x - avg_) ** 2 for x in list_) / len(list_)) ** 0.5


def tuple_stat(tuple_list: list[tuple]) -> tuple:
    """
    Recursively calculate the average and standard deviation for all the values in the given list of tuples.
    :param tuple_list: A list of tuples.
    :return: A tuple with the same length as the given tuples, but with the average and standard deviation values.
    """
    return tuple((avg(t), std(t)) for t in zip(*tuple_list))


def dict_stat(dict_list: list[dict]) -> dict:
    """
    Recursively calculate the average and standard deviation of all the values in the given list of dictionaries.
    :param dict_list: A list of dictionaries.
    :return: A dictionary with the same keys as the given dictionaries, but with the average and standard deviation values.
    """
    result = {}
    for key in dict_list[0].keys():
        # If value is str, skip
        if isinstance(dict_list[0][key], list):
            if not dict_list[0][key]:
                result[key] = []
            elif isinstance(dict_list[0][key][0], dict):
                result[key] = dict_stat(list(chain.from_iterable(d[key] for d in dict_list)))
            elif isinstance(dict_list[0][key][0], tuple):
                result[key] = tuple_stat(list(chain.from_iterable(d[key] for d in dict_list)))
        else:
            values = [d[key] for d in dict_list]
            result[key] = (avg(values), std(values))
    return result
