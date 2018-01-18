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
        self.__parm_editor.BlockRenamed.connect(self.__blockRenamed)
        self.__graph_tabs.tabCloseRequested.connect(self.__closeGraphRequest)
        self.__graph.ItemDobleClicked.connect(self.__showGraphTab)
        self.__graph.BlockDeleted.connect(self.__closeDeletedGrapgTab)
        self.__graph_tabs.currentChanged.connect(self.__currentGraphTabChanged)

    def __blockRenamed(self, bloc, newName):
        res = self.__graph.renameNode(bloc, newName)
        if res:
            return

        for subt in self.__subnets.values():
            if subt["widget"].renameNode(bloc, newName):
                return

        raise Exception, "Failed to find the node : {}".format(oldName)

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
        widget_created = False

        if self.__subnets.has_key(bloc):
            index = self.__subnets[bloc]["index"]
            if index is None:
                index = self.__graph_tabs.addTab(self.__subnets[bloc]["widget"], bloc.name())
                self.__subnets[bloc]["index"] = index
        else:
            widget_created = True
            grph = graph.SubNet(boxObject=bloc, parent=self)
            grph.ItemDobleClicked.connect(self.__showGraphTab)
            grph.CurrentNodeChanged.connect(self.__currentBlockChanged)

            index = self.__graph_tabs.addTab(grph, bloc.name())
            self.__subnets[bloc] = {}
            self.__subnets[bloc]["index"] = index
            self.__subnets[bloc]["widget"] = grph

        self.__graph_tabs.setCurrentIndex(index)

        if widget_created:
            self.__subnets[bloc]["widget"].moveProxiesToCenter()

    def __closeDeletedGrapgTab(self, bloc):
        vals = self.__subnets.get(bloc, {})
        if not vals:
            return

        widget = vals["widget"]
        widget.close()
        del widget

        if vals["index"] is not None:
            self.__graph_tabs.removeTab(vals["index"])

        self.__subnets.pop(bloc)

    def __closeGraphRequest(self, index):
        if index <= 0:
            return

        for bloc, vals in self.__subnets.iteritems():
            if vals["index"] == index:
                vals["index"] = None

        self.__graph_tabs.removeTab(index)

    def __runPressed(self):
        graph = None
        index = self.__graph_tabs.currentIndex()
        if index == 0:
            graph = self.__graph

        if graph is None:
            for vals in self.__subnets.values():
                if vals["index"] == index:
                    graph = vals["widget"]
                    break

        self.__graph.boxModel().run(perProcessCallback=graph.viewport().update)
        self.__packet_history.refresh()

    def __currentBlockChanged(self, bloc):
        if not bloc:
            self.__parm_editor.setBlock(None)
            self.__packet_history.setBlock(None)
            return

        self.__parm_editor.setBlock(bloc)
        self.__packet_history.setBlock(bloc)
