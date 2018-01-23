import os
import json
import re
import os
from . import const
import operator


RootBlockPath = re.compile("^{}\/".format(const.RootBoxName))
LastPath = re.compile("\/[^/]+$")


def PopRootPath(path):
    return RootBlockPath.sub("", path)


def AddRootPath(path):
    if RootBlockPath.search(path):
        return path

    return "{}/{}".format(const.RootBoxName, path)


def ParentPath(path):
    return LastPath.sub("", path)


def __sortDataBtPath(data):
    return sorted(data, cmp=BlockCompare, key=operator.itemgetter("path"))


def BaseName(path):
    return os.path.splitext(os.path.basename(path))[0]


def Save(path, data):
    data["blocks"] = __sortDataBtPath(data["blocks"])
    data["connections"] = __sortDataBtPath(data["connections"])
    data["proxyPorts"] = __sortDataBtPath(data["proxyPorts"])
    data["proxyParameters"] = __sortDataBtPath(data["proxyParameters"])

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    print("// Save : {}".format(path))


def Load(path):
    data = {}
    with open(path, "r") as f:
        data = json.load(f)

    print("// Load : {}".format(path))

    data["blocks"] = __sortDataBtPath(data["blocks"])
    data["connections"] = __sortDataBtPath(data["connections"])
    data["proxyPorts"] = __sortDataBtPath(data["proxyPorts"])
    data["proxyParameters"] = __sortDataBtPath(data["proxyParameters"])

    return data


def BlockCompare(x, y):
    xc = x.count("/")
    yc = y.count("/")

    return cmp(x, y) if xc == yc else cmp(xc, yc)
