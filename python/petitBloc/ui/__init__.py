

def Show(path=None):
    import sys
    import os
    from Qt import QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    win = Create()

    if path:
        if os.path.isfile(path) and os.path.splitext(path)[-1].lower() == ".blcs":
            win.openScene(path)

    win.show()

    app.exec_()


def Create(parent=None):
    from . import main
    from .. import workerManager
    from .. import const

    workerManager.WorkerManager.SetLogLevel(const.LogLevel.NoLog)
    workerManager.WorkerManager.SetUseProcess(False)

    return main.MainWindow(parent=parent)
