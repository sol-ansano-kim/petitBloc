from Qt import QtWidgets
from Qt import QtCore
from . import blockItem


class GraphScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super(GraphScene, self).__init__(parent=parent)


class Graph(QtWidgets.QGraphicsView):
    def __init__(self, model, parent=None):
        self.__model = model
        self.__scene = GraphScene()
        super(Graph, self).__init__(self.__scene, parent=parent)
        self.__initialize()

    def addBlock(self, name):
        bloc = self.__model.addBlock(name)
        if not bloc:
            return

        itm = blockItem.BlockItem(bloc)
        self.__scene.addItem(itm)


    def scene(self):
        return self.__scene

    def __initialize(self):
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setRubberBandSelectionMode(QtCore.Qt.ItemSelectionMode.IntersectsItemShape)
