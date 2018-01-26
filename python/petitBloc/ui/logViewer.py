from Qt import QtWidgets
from .. import const


class LogViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LogViewer, self).__init__(parent=parent)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        self.__time = 0
        self.__debug = []
        self.__warn = []
        self.__error = []
        self.__log_level = const.LogLevel.Error

        self.__time_view = QtWidgets.QLabel()
        layout.addWidget(QtWidgets.QLabel("Time"), 0, 0)
        layout.addWidget(self.__time_view, 0, 1)
        
        self.__error_label = QtWidgets.QLabel("Error")
        self.__error_view = QtWidgets.QTextEdit()
        self.__error_view.setReadOnly(True)
        layout.addWidget(self.__error_label, 1, 0)
        layout.addWidget(self.__error_view, 1, 1)
        
        self.__warn_label = QtWidgets.QLabel("Warning")
        self.__warn_view = QtWidgets.QTextEdit()
        self.__warn_view.setReadOnly(True)
        layout.addWidget(self.__warn_label, 2, 0)
        layout.addWidget(self.__warn_view, 2, 1)

        self.__debug_label = QtWidgets.QLabel("Debug")
        self.__debug_view = QtWidgets.QTextEdit()
        self.__debug_view.setReadOnly(True)
        layout.addWidget(self.__debug_label, 3, 0)
        layout.addWidget(self.__debug_view, 3, 1)

        self.updateViewer()

    def setLogLevel(self, l):
        if l == 0:
            self.__log_level = const.LogLevel.NoLog
        elif l == 1:
            self.__log_level = const.LogLevel.Error
        elif l == 2:
            self.__log_level = const.LogLevel.Warn
        elif l == 3:
            self.__log_level = const.LogLevel.Debug

        self.updateViewer()

    def clear(self):
        self.__time = 0
        self.__debug = []
        self.__warn = []
        self.__error = []
        self.updateViewer()

    def updateViewer(self):
        self.__time_view.setText("{} Sec".format(round(self.__time, 4)))
        self.__error_view.setText("\n".join(self.__error))
        self.__warn_view.setText("\n".join(self.__warn))
        self.__debug_view.setText("\n".join(self.__debug))

        if self.__log_level >= const.LogLevel.Debug:
            self.__debug_label.show()
            self.__debug_view.show()
        else:
            self.__debug_label.hide()
            self.__debug_view.hide()

        if self.__log_level >= const.LogLevel.Warn:
            self.__warn_label.show()
            self.__warn_view.show()
        else:
            self.__warn_label.hide()
            self.__warn_view.hide()

        if self.__log_level >= const.LogLevel.Error:
            self.__error_label.show()
            self.__error_view.show()
        else:
            self.__error_label.hide()
            self.__error_view.hide()

    def setLogs(self, time, debug, warn, error):
        self.__time = time
        self.__debug = debug
        self.__warn = warn
        self.__error = error

        self.updateViewer()
