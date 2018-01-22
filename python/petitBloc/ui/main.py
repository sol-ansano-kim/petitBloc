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
        self.__networks = {}
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
        self.__networks[self.__graph.box()] = {"graph": self.__graph, "init": False}

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
        self.__resetTabIndice()

        self.__run.clicked.connect(self.__runPressed)

        self.__graph_tabs.tabCloseRequested.connect(self.__closeGraphRequest)
        self.__graph_tabs.currentChanged.connect(self.__currentGraphTabChanged)

        self.__parm_editor.BlockRenamed.connect(self.__blockRenamed)

        self.__graph.CurrentNodeChanged.connect(self.__currentBlockChanged)
        self.__graph.ItemDobleClicked.connect(self.__showGraphTab)
        self.__graph.BoxDeleted.connect(self.__boxDeleted)

        self.__graph.BoxCreated.connect(self.__boxCreated)

    def __blockRenamed(self, bloc, newName):
        for n_dict in self.__networks.values():
            if n_dict["graph"].renameNode(bloc, newName):
                return

        raise Exception, "Failed to find the node : {}".format(oldName)

    def __currentGraphTabChanged(self, index):
        widget = None

        for n_dict in self.__networks.values():
            if n_dict.get("index", None) == index:
                widget = n_dict["graph"]
                break

        if widget is None:
            return

        self.__parm_editor.allowProxy(index != 0)
        self.__currentBlockChanged(widget.currentBlock())

    def __boxCreated(self, boxBloc, init=True):
        if self.__networks.has_key(boxBloc):
            return

        grph = graph.SubNet(boxObject=boxBloc)
        grph.ItemDobleClicked.connect(self.__showGraphTab)
        grph.CurrentNodeChanged.connect(self.__currentBlockChanged)
        grph.BoxDeleted.connect(self.__boxDeleted)
        grph.ProxyPortAdded.connect(self.__addProxyPort)
        grph.ProxyPortRemoved.connect(self.__removeProxyPort)
        grph.BoxCreated.connect(self.__boxCreated)

        self.__networks[boxBloc] = {"graph": grph, "init": init}

    def __showGraphTab(self, bloc):
        widget_created = False

        box_data = self.__networks[bloc]

        if box_data.get("index") is None:
            widget_created = True
            index = self.__graph_tabs.addTab(self.__networks[bloc]["graph"], bloc.path())
            self.__networks[bloc]["index"] = index

        self.__graph_tabs.setCurrentIndex(self.__networks[bloc]["index"])

        if self.__networks[bloc]["init"]:
            self.__networks[bloc]["graph"].initProxyNode()
            self.__networks[bloc]["init"] = False

    def __boxDeleted(self, bloc):
        path = bloc.path()

        remove_blocs = []
        remove_widgets = []
        remove_indices = []

        for bloc, n_dict in self.__networks.iteritems():
            if bloc.path().startswith(path):
                remove_blocs.append(bloc)
                widget = n_dict.get("graph")
                index = n_dict.get("index")
                if widget is not None:
                    remove_widgets.append(widget)

                if index is not None:
                    remove_indices.append(index)

        remove_indices.sort()
        remove_indices.reverse()

        while (remove_indices):
            index = remove_indices.pop(0)
            self.__graph_tabs.removeTab(index)

        while (remove_blocs):
            bloc = remove_blocs.pop(0)
            self.__networks.pop(bloc, None)

        while (remove_widgets):
            widget = remove_widgets.pop(0)
            widget.close()
            del widget

        self.__resetTabIndice()

    def __closeGraphRequest(self, index):
        if index <= 0:
            return

        self.__graph_tabs.removeTab(index)
        self.__resetTabIndice()

    def __resetTabIndice(self):
        for n_dict in self.__networks.values():
            index = self.__graph_tabs.indexOf(n_dict["graph"])
            n_dict["index"] = None if index < 0 else index

    def __addProxyPort(self, boxBloc, proxyNode, port):
        par_dict = self.__networks.get(boxBloc.parent(), None)

        if not par_dict:
            return

        node = par_dict["graph"].findNode(boxBloc)

        if port.isInPort():
            par_dict["graph"].createAttribute(node=node, port=port, plug=False, socket=True, preset="attr_preset_1", dataType=port.typeClass(), proxyNode=proxyNode)
        else:
            par_dict["graph"].createAttribute(node=node, port=port, plug=True, socket=False, preset="attr_preset_1", dataType=port.typeClass(), proxyNode=proxyNode)

    def __removeProxyPort(self, boxBloc, proxyNode, name):
        par_dict = self.__networks.get(boxBloc.parent(), None)
        if not par_dict:
            return

        node = par_dict["graph"].findNode(boxBloc)

        par_dict["graph"].deleteAttribute(node, node.attrs.index(name))

    def __runPressed(self):
        graph = None
        index = self.__graph_tabs.currentIndex()

        for n_dict in self.__networks.values():
            if n_dict["index"] == index:
                graph = n_dict["graph"]
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
