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
        self.__removed_subnets = []
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

        self.__graph_tabs.tabCloseRequested.connect(self.__closeGraphRequest)
        self.__graph_tabs.currentChanged.connect(self.__currentGraphTabChanged)

        self.__parm_editor.BlockRenamed.connect(self.__blockRenamed)

        self.__graph.CurrentNodeChanged.connect(self.__currentBlockChanged)
        self.__graph.ItemDobleClicked.connect(self.__showGraphTab)
        self.__graph.BoxDeleted.connect(self.__boxDeleted)

        self.__graph.BoxCreated.connect(self.__boxCreated)

    def __blockRenamed(self, bloc, newName):
        res = self.__graph.renameNode(bloc, newName)
        if res:
            return

        for subt in self.__subnets.values():
            if subt["widget"].renameNode(bloc, newName):
                return

        raise Exception, "Failed to find the node : {}".format(oldName)

    def __currentGraphTabChanged(self, index):
        allowProxy = True
        widget = None
        if index == 0:
            widget = self.__graph
            allowProxy = False

        if widget is None:
            for bloc, vals in self.__subnets.iteritems():
                if vals.get("index", None) == index:
                    widget = vals["widget"]
                    break

        self.__parm_editor.allowProxy(allowProxy)
        self.__currentBlockChanged(widget.currentBlock())

    def __boxCreated(self, boxBloc, parent, init=True):
        if self.__subnets.has_key(boxBloc):
            return

        grph = graph.SubNet(boxObject=boxBloc, parent=parent)
        grph.ItemDobleClicked.connect(self.__showGraphTab)
        grph.CurrentNodeChanged.connect(self.__currentBlockChanged)
        grph.BoxDeleted.connect(self.__boxDeleted)
        grph.ProxyPortAdded.connect(self.__addProxyPort)
        grph.ProxyPortRemoved.connect(self.__removeProxyPort)
        grph.BoxCreated.connect(self.__boxCreated)

        self.__subnets[boxBloc] = {"parentWidget": parent, "widget": grph, "init": init}

    def __showGraphTab(self, bloc):
        widget_created = False

        box_data = self.__subnets[bloc]

        if box_data.get("index") is None:
            widget_created = True
            index = self.__graph_tabs.addTab(self.__subnets[bloc]["widget"], bloc.path())
            self.__subnets[bloc]["index"] = index

        self.__graph_tabs.setCurrentIndex(self.__subnets[bloc]["index"])

        if self.__subnets[bloc]["init"]:
            self.__subnets[bloc]["widget"].moveProxiesToCenter()
            self.__subnets[bloc]["init"] = False

    def __boxDeleted(self, bloc):
        self.__removed_subnets = [bloc]

        self.__closeDeletedGraphTab(bloc)

        for s in self.__removed_subnets:
            self.__subnets.pop(s)

    def __closeDeletedGraphTab(self, bloc):
        vals = self.__subnets.get(bloc, {})
        if not vals:
            return

        widget = vals.get("widget")

        for sub_bloc, sub_vals in self.__subnets.iteritems():
            if sub_vals["parentWidget"] == widget:
                self.__closeDeletedGraphTab(sub_bloc)

        widget.close()
        del widget

        if vals.get("index", None) is not None:
            self.__graph_tabs.removeTab(vals["index"])

        self.__resetTabIndice()

    def __closeGraphRequest(self, index):
        if index <= 0:
            return

        self.__graph_tabs.removeTab(index)
        self.__resetTabIndice()

    def __resetTabIndice(self):
        for vals in self.__subnets.values():
            index = self.__graph_tabs.indexOf(vals.get("widget"))
            vals["index"] = None if index < 0 else index

    def __addProxyPort(self, boxBloc, proxyNode, port):
        par_grp = self.__subnets.get(boxBloc, {}).get("parentWidget")
        if not par_grp:
            return

        node = par_grp.findNode(boxBloc)

        if port.isInPort():
            par_grp.createAttribute(node=node, port=port, plug=False, socket=True, preset="attr_preset_1", dataType=port.typeClass(), proxyNode=proxyNode)
        else:
            par_grp.createAttribute(node=node, port=port, plug=True, socket=False, preset="attr_preset_1", dataType=port.typeClass(), proxyNode=proxyNode)

    def __removeProxyPort(self, boxBloc, proxyNode, name):
        par_grp = self.__subnets.get(boxBloc, {}).get("parentWidget")
        if not par_grp:
            return

        node = par_grp.findNode(boxBloc)

        par_grp.deleteAttribute(node, node.attrs.index(name))

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
