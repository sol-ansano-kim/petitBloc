from Qt import QtGui
from . import const


__Toolset = None


class Toolset(object):
    def __init__(self):
        self.__pens = {}
        self.__pens["default"] = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.__pens["blockline_normal"] = QtGui.QPen(QtGui.QColor(125, 125, 125))
        self.__pens["blockline_normal"].setWidth(const.LineWidth)
        self.__pens["blockline_selected"] = QtGui.QPen(QtGui.QColor(70, 233, 154))
        self.__pens["blockline_selected"].setWidth(const.LineWidth)
        self.__pens["text_normal"] = QtGui.QPen(QtGui.QColor(225, 225, 225))
        self.__pens["blocklabel_normal"] = QtGui.QPen(QtGui.QColor(225, 225, 225))
        self.__pens["port_float"] = QtGui.QPen(QtGui.QColor(96, 194, 121))
        self.__pens["port_bool"] = QtGui.QPen(QtGui.QColor(153, 179, 229))
        self.__pens["port_int"] = QtGui.QPen(QtGui.QColor(69, 181, 255))
        self.__pens["port_str"] = QtGui.QPen(QtGui.QColor(241, 119, 54))
        self.__pens["port_other"] = QtGui.QPen(QtGui.QColor(175, 175, 175))

        self.__brushes = {}
        self.__brushes["default"] = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        self.__brushes["blockbody_normal"] = QtGui.QBrush(QtGui.QColor(75, 75, 75))
        self.__brushes["port_float"] = QtGui.QBrush(QtGui.QColor(96, 194, 121))
        self.__brushes["port_bool"] = QtGui.QBrush(QtGui.QColor(153, 179, 229))
        self.__brushes["port_int"] = QtGui.QBrush(QtGui.QColor(69, 181, 255))
        self.__brushes["port_str"] = QtGui.QBrush(QtGui.QColor(241, 119, 54))
        self.__brushes["port_other"] = QtGui.QBrush(QtGui.QColor(175, 175, 175))

    def getPen(self, name):
        return self.__pens.get(name, self.__pens["default"])

    def getBrush(self, name):
        return self.__brushes.get(name, self.__brushes["default"])


def __GetToolset():
    global __Toolset
    if __Toolset is None:
        __Toolset = Toolset()

    return __Toolset


def GetPen(name):
    toolset = __GetToolset()
    return toolset.getPen(name)


def GetBrush(name):
    toolset = __GetToolset()
    return toolset.getBrush(name)
