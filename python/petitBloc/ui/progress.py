from Qt import QtWidgets
from Qt import QtCore


class ProgressManager(object):
    def __init__(self, parent):
        self.__parent = parent
        self.__progress = 0
        self.__increase = 0
        self.__accumulation = 0

    def reset(self):
        self.setProgress(0)
        self.__accumulation = 0

    def setCount(self, count):
        if count == 0:
            self.__increase = 100

        else:
            self.__increase = 100 / float(count)

    def setProgress(self, v, update=False):
        self.__progress = v
        self.__parent.setValue(int(self.__progress), update)

    def increase(self):
        self.__accumulation += self.__increase
        update = False
        if self.__accumulation >= 10:
            update = True
            self.__accumulation = 0

        self.setProgress(self.__progress + self.__increase, update)


class Progress(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(Progress, self).__init__(parent)
        self.__manager = ProgressManager(self)
        self.setObjectName("ProgressFrame")

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        layout.setSpacing(30)
        self.setLayout(layout)

        status = QtWidgets.QLabel("Please Wait...")
        status.setObjectName("TransparentLabel")
        status.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        status.setFixedSize(200, 50)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setValue(0)
        self.progress.setMinimumWidth(100)
        self.progress.setMaximumWidth(200)

        layout.addWidget(status)
        layout.addWidget(self.progress)

    def manager(self):
        return self.__manager

    def setValue(self, v, update=False):
        self.progress.setValue(v)

        if update:
            QtCore.QCoreApplication.processEvents()
