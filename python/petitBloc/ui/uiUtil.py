import os
import re
from . import const
from Nodz import nodz_utils
from Qt import QtGui


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


def __clamp(v):
    if v < 0:
        return 0
    elif v > 255:
        return 255

    return v


def ConvertDataToColor(data=None, alternate=False, av=20):
    if len(data) == 3:
        color = QtGui.QColor(data[0], data[1], data[2])
        if alternate:
            mult = nodz_utils._generateAlternateColorMultiplier(color, av)


            color = QtGui.QColor(__clamp(data[0]-(av*mult)), __clamp(data[1]-(av*mult)), __clamp(data[2]-(av*mult)))
        return color

    # rgba
    elif len(data) == 4:
        color = QtGui.QColor(data[0], data[1], data[2], data[3])
        if alternate:
            mult = nodz_utils._generateAlternateColorMultiplier(color, av)
            color = QtGui.QColor(__clamp(data[0]-(av*mult)), __clamp(data[1]-(av*mult)), __clamp(data[2]-(av*mult)), data[3])
        return color

    # wrong
    else:
        print 'Color from configuration is not recognized : ', data
        print 'Can only be [R, G, B] or [R, G, B, A]'
        print 'Using default color !'
        color = QtGui.QColor(120, 120, 120)
        if alternate:
            av = av if av < 120 else 120
            color = QtGui.QColor(120-av, 120-av, 120-av)
        return color
