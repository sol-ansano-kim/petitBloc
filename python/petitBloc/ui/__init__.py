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
        if os.path.isfile(path) and os.path.splitext(path)[-1].lower() == ".blcs":
            win.openScene(path)

    win.show()

    app.exec_()


def Create(parent=None):
    from . import main
    return main.MainWindow(parent=parent)
