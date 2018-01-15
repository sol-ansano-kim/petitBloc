from Qt import QtWidgets
from .Nodz import nodz_main
from . import const


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.__initialize()

    def __initialize(self):
        centeral = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        self.setCentralWidget(centeral)
        centeral.setLayout(main_layout)
        self.__nodz = nodz_main.Nodz(parent=self)
        self.__nodz.initialize()
        main_layout.addWidget(self.__nodz)
        self.setWindowTitle(const.WindowTitle)
        self.setObjectName(const.ObjectName)
