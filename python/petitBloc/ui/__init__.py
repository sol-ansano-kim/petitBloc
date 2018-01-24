import external


def Show(path=None, multiProcessing=False):
    import sys
    import os
    from Qt import QtWidgets
    from petitBloc import workerManager

    workerManager.WorkerManager.SetUseProcess(multiProcessing)

    app = QtWidgets.QApplication(sys.argv)
    win = Create()

    if path is not None:
        if lower(os.path.splitext(path)[-1]) == ".blcs":
            win.load(path)

    win.show()

    app.exec_()


def Create(parent=None):
    from . import main
    return main.MainWindow(parent=parent)
