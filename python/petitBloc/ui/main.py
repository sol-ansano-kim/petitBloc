from Qt import QtWidgets
from Qt import QtCore
from Qt import QtGui
from .Nodz import nodz_main
from . import const
from . import model
from . import graph
from . import paramEditor
from . import packetHistory


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.__graph = None
        self.__graph_tabs = None
        self.__editor_tabs = None
        self.__run = None
        self.__parm_editor = None
        self.__subnets = {}
        self.__initialize()

    def __initialize(self):
        self.setWindowTitle(const.WindowTitle)
        self.setObjectName(const.ObjectName)

        centeral = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        self.setCentralWidget(centeral)
        centeral.setLayout(main_layout)

        self.__editor_tabs = QtWidgets.QTabWidget()
        self.__graph_tabs = QtWidgets.QTabWidget()
        self.__graph_tabs.setTabsClosable(True)

        self.__graph = graph.Graph(name="scene", parent=self)
        self.__graph.initialize()
        self.__graph_tabs.addTab(self.__graph, "Scene")
        self.__graph_tabs.tabBar().tabButton(0, QtWidgets.QTabBar.RightSide).hide()

        self.__parm_editor = paramEditor.ParamEditor()
        self.__packet_history = packetHistory.PacketHistory()
        self.__editor_tabs.addTab(self.__parm_editor, "Param Editor")
        self.__editor_tabs.addTab(self.__packet_history, "Packet History")

        self.__run = QtWidgets.QPushButton("RUN")

        main_contents = QtWidgets.QSplitter()
        main_contents.addWidget(self.__graph_tabs)
        main_contents.addWidget(self.__editor_tabs)

        main_layout.addWidget(main_contents)
        main_layout.addWidget(self.__run)

        self.__run.clicked.connect(self.__runPressed)
        self.__graph.CurrentNodeChanged.connect(self.__currentBlockChanged)
        self.__parm_editor.BlockRenamed.connect(self.__graph.renameNode)
        self.__graph_tabs.tabCloseRequested.connect(self.__closeGraphRequest)
        self.__graph.ItemDobleClicked.connect(self.__showGraphTab)
        self.__graph.BlockDeleted.connect(self.__closeDeletedGrapgTab)
        self.__graph_tabs.currentChanged.connect(self.__currentGraphTabChanged)

    def __currentGraphTabChanged(self, index):
        widget = None
        if index == 0:
            widget = self.__graph

        if widget is None:
            for bloc, vals in self.__subnets.iteritems():
                if vals["index"] == index:
                    widget = vals["widget"]
                    break

        self.__currentBlockChanged(widget.currentBlock())

    def __showGraphTab(self, bloc):
        if self.__subnets.has_key(bloc):
            index = self.__subnets[bloc]["index"]

        else:
            grph = graph.Graph(boxObject=bloc, parent=self)
            grph.initialize()
            index = self.__graph_tabs.addTab(grph, bloc.name())

            self.__subnets[bloc] = {}
            self.__subnets[bloc]["index"] = index
            self.__subnets[bloc]["widget"] = grph
            grph.ItemDobleClicked.connect(self.__showGraphTab)
            grph.CurrentNodeChanged.connect(self.__currentBlockChanged)

        self.__graph_tabs.setCurrentIndex(index)

    def __closeDeletedGrapgTab(self, bloc):
        vals = self.__subnets.get(bloc, {})
        if not vals:
            return

        widget = vals["widget"]
        widget.close()
        del widget
        self.__subnets.pop(bloc)
        self.__graph_tabs.removeTab(vals["index"])

    def __closeGraphRequest(self, index):
        if index <= 0:
            return

        widget = None
        creator = None
        t_bloc = None
        for bloc, vals in self.__subnets.iteritems():
            if vals["index"] == index:
                widget = vals["widget"]
                t_bloc = bloc

        widget.close()
        del widget
        self.__subnets.pop(t_bloc)
        self.__graph_tabs.removeTab(index)

    def __runPressed(self):
        self.__graph.boxModel().run(perProcessCallback=self.__graph.viewport().update)
        self.__packet_history.refresh()

    def __currentBlockChanged(self, bloc):
        if not bloc:
            self.__parm_editor.setBlock(None)
            self.__packet_history.setBlock(None)
            return

        self.__parm_editor.setBlock(bloc)
        self.__packet_history.setBlock(bloc)
