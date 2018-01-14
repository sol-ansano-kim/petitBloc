from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from . import const
from . import toolset


class PortItem(object):
    def __init__(self, model, parent=None):
        super(PortItem, self).__init__()
        self.__model = model
        self.__parent = parent
        self.__brush = None
        self.__pen = None
        self.__x = 0
        self.__y = 0
        self.__initialize()

    def setPos(self, x, y):
        self.__x = x
        self.__y = y

    def pos(self):
        return self.__x, self.__y

    def draw(self, painter, option, blockWidth, y):
        painter.save()

        font = painter.font()
        font.setPointSize(const.PortSize)
        painter.setFont(font)
        font_mat = QtGui.QFontMetrics(font)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self.__brush)

        px = 0 if self.__model.isInPort() else (blockWidth)
        port_half = const.PortSize * 0.5

        painter.drawEllipse(px, y - port_half, const.PortSize, const.PortSize)

        painter.setPen(self.__pen)

        if self.__model.isInPort():
            painter.drawText(px + const.PortSize + 4, y + port_half, font_mat.elidedText(self.__model.name(), QtCore.Qt.ElideRight, blockWidth))
        else:
            painter.drawText(px - font_mat.width(self.__model.name()) - 4, y + port_half, font_mat.elidedText(self.__model.name(), QtCore.Qt.ElideRight, blockWidth))

        painter.restore()

    def __initialize(self):
        t = self.__model.type()
        if t is int:
            b = toolset.GetBrush("port_int")
            p = toolset.GetPen("port_int")
        elif t is float:
            b = toolset.GetBrush("port_float")
            p = toolset.GetPen("port_float")
        elif t is bool:
            b = toolset.GetBrush("port_bool")
            p = toolset.GetPen("port_bool")
        elif issubclass(t, basestring):
            b = toolset.GetBrush("port_str")
            p = toolset.GetPen("port_str")
        else:
            b = toolset.GetBrush("port_other")
            p = toolset.GetPen("port_other")

        self.__brush = b
        self.__pen = p


class BlockItem(QtWidgets.QGraphicsItem):
    def __init__(self, model, parent=None):
        super(BlockItem, self).__init__(parent=parent)
        self.__model = model
        self.__width = const.BlockWidth
        self.__height = const.BlockDefaultHeight
        self.__body_brush = toolset.GetBrush("blockbody_normal") 
        self.__ports = []
        self.__initialize()

    def __initialize(self):
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setZValue(const.BlockDepth)
        self.setPorts()

    def setPorts(self):
        self.__ports = []

        inputs = self.__model.inputs()
        outputs = self.__model.outputs()

        s = len(inputs) + len(outputs)
        if s <= 1:
            self.__height = const.BlockDefaultHeight
        else:
            self.__height = const.BlockDefaultHeight + (s * (const.PortSize + 4))
            
        self.__ports = map(lambda x: PortItem(x), inputs + outputs)

    def boundingRect(self):
        return QtCore.QRect(0, 0, self.__width, self.__height)

    def paint(self, painter, option, widget=None):
        painter.save()

        font = painter.font()

        # draw body
        painter.setBrush(self.__body_brush)
        if (option.state & QtWidgets.QStyle.State_Selected):
            painter.setPen(toolset.GetPen("blockline_selected"))
        else:
            painter.setPen(toolset.GetPen("blockline_normal"))

        mar = const.BlockNameFontSize + 5
        bloc_height = self.__height - mar
        bloc_width = self.__width - const.PortSize

        painter.drawRoundedRect(const.PortSize * 0.5, mar, bloc_width, bloc_height, const.BlockRound, const.BlockRound)

        # draw ports
        stp = bloc_height / (len(self.__ports) + 1)

        for i, port in enumerate(self.__ports):
            py = (stp * (i + 1)) + mar
            port.draw(painter, option, bloc_width, py)

        font.setPointSize(const.BlockNameFontSize)
        painter.setFont(font)
        painter.setPen(toolset.GetPen("text_normal"))
        painter.drawText(0, const.BlockNameFontSize, QtGui.QFontMetrics(font).elidedText(self.__model.name(), QtCore.Qt.ElideRight, self.__width))

        painter.restore()
