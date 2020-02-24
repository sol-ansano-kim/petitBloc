from Qt import QtWidgets
from Qt import QtCore
import pprint


class PacketModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super(PacketModel, self).__init__(parent=parent)
        self.__bloc = None
        self.__ports = []
        self.__packets = {}
        self.__row = 0
        self.__col = 0
        self.__max_size = -1

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled

    def headerData(self, section, orient, role):
        if role != QtCore.Qt.DisplayRole:
            return None

        if orient == QtCore.Qt.Vertical:
            return str(section)

        if orient == QtCore.Qt.Horizontal and (section >= 0 and section <= self.__col):
            return self.__ports[section]

        return None

    def setMaxSize(self, v):
        self.__max_size = v

    def rowCount(self, parent=None):
        return self.__row

    def columnCount(self, parent=None):
        return self.__col

    def data(self, index, role):
        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter

        if role != QtCore.Qt.DisplayRole:
            return None

        col = index.column()
        row = index.row()

        if col < 0 or row < 0:
            return None

        if col >= len(self.__ports):
            return None

        vals = self.__packets[self.__ports[col]]

        if row >= len(vals):
            return None

        return pprint.pformat(vals[row])

    def setBlock(self, bloc):
        self.__bloc = bloc
        self.refresh()

    def refresh(self):
        self.beginResetModel()
        self.__ports = []
        self.__packets = {}
        self.__row = 0
        self.__col = 0

        if self.__bloc is not None:
            ports = []

            if self.__bloc.hasNetwork():
                for ip in self.__bloc.inputProxies():
                    ports.append((ip.name(), ip.proxySource()))

                for op in self.__bloc.outputProxies():
                    ports.append((op.name(), op.proxySource()))

            for p in self.__bloc.inputs():
                ports.append((p.name(), p))

            for p in self.__bloc.outputs():
                ports.append((p.name(), p))

            for name, p in ports:
                if name == "success":
                    continue

                self.__ports.append(name)
                self.__col += 1

                if p is None:
                    self.__packets[name] = []
                    continue

                vals = p.packetHistory()
                if len(vals) > self.__row:
                    if self.__max_size >= 0 and self.__max_size < len(vals):
                        self.__row = self.__max_size
                    else:
                        self.__row = len(vals)

                self.__packets[name] = vals

        self.endResetModel()


class PacketView(QtWidgets.QTableView):
    def __init__(self, parent=None):
        super(PacketView, self).__init__(parent=parent)
        self.__model = None
        self.__initialize()

    def __initialize(self):
        self.__model = PacketModel()
        self.setModel(self.__model)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    def setMaxSize(self, v):
        self.__model.setMaxSize(v)

    def setBlock(self, bloc):
        self.__model.setBlock(bloc)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def refresh(self):
        self.__model.refresh()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


class PacketHistory(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PacketHistory, self).__init__(parent=parent)
        self.__block = None
        self.__packet_view = None
        self.__initialize()

    def setBlock(self, bloc):
        self.__block = bloc
        self.__packet_view.setBlock(bloc)

    def setMaxSize(self, v):
        self.__packet_view.setMaxSize(v)
        self.__packet_view.refresh()

    def refresh(self):
        self.__packet_view.refresh()

    def __initialize(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setLayout(main_layout)

        label = QtWidgets.QLabel("PacketHistory")
        label.setAlignment(QtCore.Qt.AlignCenter)
        self.__packet_view = PacketView()

        main_layout.addWidget(label)
        main_layout.addWidget(self.__packet_view)
