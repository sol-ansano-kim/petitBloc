from Qt import QtWidgets
from Qt import QtCore


class SceneState(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SceneState, self).__init__(parent=parent)
        self.__exe_count = 0
        self.__error_count = 0
        self.__total_time = 0.0
        self.__avg_time = 0.0
        self.__exe_label = None
        self.__error_label = None
        self.__time_label = None
        self.__avg_label = None

        self.__initialize()
        self.__updateUI()

    def __updateUI(self):
        self.__exe_label.setText("Execution : {}".format(self.__exe_count))
        self.__error_label.setText("Error : {}".format(self.__error_count))
        self.__time_label.setText("Total Time : {}".format(round(self.__total_time, 4)))
        self.__avg_label.setText("Avg time : {}".format(round(self.__avg_time, 4)))

    def setStates(self, exeCount, errorCount, totalTime, avgTime):
        self.__exe_count = exeCount
        self.__error_count = errorCount
        self.__total_time = totalTime
        self.__avg_time = avgTime
        self.__updateUI()

    def __initialize(self):
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        self.__exe_label = QtWidgets.QLabel()
        self.__error_label = QtWidgets.QLabel()
        self.__time_label = QtWidgets.QLabel()
        self.__avg_label = QtWidgets.QLabel()
        self.__exe_label.setObjectName("StateLabel")
        self.__error_label.setObjectName("StateLabel")
        self.__time_label.setObjectName("StateLabel")
        self.__avg_label.setObjectName("StateLabel")

        layout.addStretch(10)
        layout.addWidget(self.__exe_label)
        layout.addWidget(self.__error_label)
        layout.addWidget(self.__time_label)
        layout.addWidget(self.__avg_label)
        layout.setAlignment(QtCore.Qt.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setFixedHeight(20)
