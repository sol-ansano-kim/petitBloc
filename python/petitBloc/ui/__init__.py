import external


def Show(path=None, multiProcessing=False):
    import sys
    import os
    from Qt import QtWidgets
    UseMultiprocessing(multiProcessing)

    app = QtWidgets.QApplication(sys.argv)
    win = Create()

    if path:
        if os.path.isfile(path) and os.path.splitext(path)[-1].lower() == ".blcs":
            win.openScene(path)

    win.show()

    app.exec_()


def UseMultiprocessing(v):
    from .. import workerManager

    workerManager.WorkerManager.SetUseProcess(v)


def Create(parent=None):
    from . import main
    return main.MainWindow(parent=parent)
