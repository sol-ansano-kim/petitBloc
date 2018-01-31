import os
import re
from . import const


RootBlockPath = re.compile("^[/]{}[/]".format(const.RootBoxName))
LastPath = re.compile("[/][^/]+$")


def GetIcon(name):
    path = os.path.abspath(os.path.join(__file__, "../icons/{}.png".format(name)))

    return path if os.path.isfile(path) else ""


def PopRootPath(path):
    return RootBlockPath.sub("", path)


def AddRootPath(path):
    if RootBlockPath.search(path):
        return path

    return "/{}/{}".format(const.RootBoxName, path)


def ParentPath(path):
    return LastPath.sub("", path)


def BaseName(path):
    return os.path.splitext(os.path.basename(path))[0]
