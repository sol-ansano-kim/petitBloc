from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from .Nodz import nodz_main
from . import const
from . import model
from . import graph
from . import blockCreator
from . import paramEditor
from . import packetHistory


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.__graph = None
        self.__creator = None
        self.__tabs = None
        self.__run = None
        self.__parm_editor = None
        self.__initialize()

    def __initialize(self):
        self.setWindowTitle(const.WindowTitle)
        self.setObjectName(const.ObjectName)

        centeral = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        self.setCentralWidget(centeral)
        centeral.setLayout(main_layout)

        md = model.BoxModel("scene")
        self.__graph = graph.Graph(md, parent=self)
        self.__graph.initialize()

        self.__tabs = QtWidgets.QTabWidget()

        self.__parm_editor = paramEditor.ParamEditor()
        self.__packet_history = packetHistory.PacketHistory()
        self.__tabs.addTab(self.__parm_editor, "Param Editor")
        self.__tabs.addTab(self.__packet_history, "Packet History")

        self.__run = QtWidgets.QPushButton("RUN")

        main_contents = QtWidgets.QSplitter()
        main_contents.addWidget(self.__graph)
        main_contents.addWidget(self.__tabs)

        main_layout.addWidget(main_contents)
        main_layout.addWidget(self.__run)

        self.__creator = blockCreator.BlockCreator(self.__graph, md.blockClassNames())

        self.__creator.BlockCreatorEnd.connect(self.addBlock)
        self.__graph.KeyPressed.connect(self.__keyPressed)
        self.__run.clicked.connect(self.__runPressed)
        self.__graph.signal_NodeSelected.connect(self.__nodeSelected)
        self.__parm_editor.BlockRenamed.connect(self.__graph.renameNode)

    def __runPressed(self):
        self.__graph.boxModel().run(perProcessCallback=self.__graph.viewport().update)
        self.__packet_history.refresh()

    def __nodeSelected(self, nodes):
        if not nodes:
            self.__parm_editor.setBlock(None)
            self.__packet_history.setBlock(None)
            return

        node = nodes[0]
        bloc = self.__graph.boxModel().block(node)
        if not bloc:
            self.__parm_editor.setBlock(None)
            self.__packet_history.setBlock(None)
            return

        self.__parm_editor.setBlock(bloc)
        self.__packet_history.setBlock(bloc)

    def __keyPressed(self, key):
        if key == QtCore.Qt.Key_Tab:
            self.__creator.show(self.__graph.mapFromGlobal(QtGui.QCursor.pos()))

    def addBlock(self, blockName):
        self.__graph.addBlock(blockName)
