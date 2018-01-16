from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from .Nodz import nodz_main
from . import const
from . import model
from . import graph
from . import blockCreator


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.__graph = None
        self.__tab = None
        self.__run = None
        self.__initialize()

    def __initialize(self):
        centeral = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        self.setCentralWidget(centeral)
        centeral.setLayout(main_layout)
        md = model.BoxModel("scene")
        self.__graph = graph.Graph(md, parent=self)
        self.__graph.initialize()
        self.__graph.signal_KeyPressed.connect(self.__key_press)
        self.__tab = blockCreator.BlockCreator(self.__graph, md.blockClassNames())
        self.__tab.BlockCreatorEnd.connect(self.addBlock)
        self.__run = QtWidgets.QPushButton("RUN")
        main_layout.addWidget(self.__graph)
        main_layout.addWidget(self.__run)
        self.setWindowTitle(const.WindowTitle)
        self.setObjectName(const.ObjectName)

        self.__run.clicked.connect(self.__graph.boxModel().run)

    def __key_press(self, key):
        if key == QtCore.Qt.Key_Tab:
            self.__tab.show(self.__graph.mapFromGlobal(QtGui.QCursor.pos()))

    def addBlock(self, blockName):
        self.__graph.addBlock(blockName)
