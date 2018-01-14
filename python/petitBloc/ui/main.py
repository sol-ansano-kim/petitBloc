import os
from Qt import QtWidgets
from Qt import QtCore
from . import const
from . import graph
from . import model


class TabLine(QtWidgets.QLineEdit):
    TabEnd = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(TabLine, self).__init__(parent=parent)
        self.setFixedWidth(100)
        self.hide()
        self.editingFinished.connect(self.send)
        self.blockSignals(True)

    def setBlockList(self, block_list):
        comple = QtWidgets.QCompleter(block_list)
        comple.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompleter(comple)

    def show(self):        
        self.setText("")
        self.blockSignals(False)
        self.setFocus(QtCore.Qt.PopupFocusReason)
        super(TabLine, self).show()

    def send(self):
        self.TabEnd.emit(self.text())
        self.blockSignals(True)
        self.hide()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.__graph = None
        self.__scene = None
        self.__scene_model = None
        self.__cursor_pos = None
        self.__tab = None
        self.__initialize()
        self.__setStyleSheet()        

    def __initialize(self):
        center = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        center.setLayout(main_layout)

        self.setCentralWidget(center)
        self.setObjectName(const.UIName)
        self.setWindowTitle(const.UITitle)

        self.__scene_model = model.BoxModel("scene")
        self.__graph = graph.Graph(self.__scene_model)
        main_layout.addWidget(self.__graph)

        self.__tab = TabLine(self)
        self.__tab.setBlockList(self.__scene_model.blockNames())

        self.installEventFilter(self)

        self.__tab.TabEnd.connect(self.addBlock)

    def __setStyleSheet(self):
        qss_path = os.path.abspath(os.path.join(__file__, "../style.qss"))

        if not os.path.isfile(qss_path):
            return

        current_dir = os.path.dirname(__file__)

        style = ""
        with open(qss_path, "r") as f:
            style = f.read()
            style = style.replace('url("', 'url("%s/' % current_dir.replace("\\", "/"))

        self.setStyleSheet(style)

    def eventFilter(self, obj, evnt):
        etype = evnt.type()
        if etype is QtCore.QEvent.Type.HoverMove:
            self.__cursor_pos = evnt.pos()
        if etype is QtCore.QEvent.Type.Leave or etype is QtCore.QEvent.Type.HoverLeave:
            self.__cursor_pos = None
        return False

    def keyPressEvent(self, evnt):
        if evnt.key() == QtCore.Qt.Key_Tab:
            if self.__cursor_pos is not None:
                self.__tab.move(self.__cursor_pos.x() + 10, self.__cursor_pos.y() + 10)
                self.__tab.show()

        super(MainWindow, self).keyPressEvent(evnt)

    def addBlock(self, name):
        self.__graph.addBlock(name)
