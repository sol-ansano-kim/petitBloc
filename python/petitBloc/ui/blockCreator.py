from Qt import QtWidgets
from Qt import QtCore


class BlockCreator(QtWidgets.QLineEdit):
    BlockCreatorEnd = QtCore.Signal(str)

    def __init__(self, parent=None, blockList=None, excludeList=None):
        super(BlockCreator, self).__init__(parent=parent)
        self.setObjectName("BlockCreator")
        if excludeList is None:
            excludeList = []
        if blockList is None:
            blockList = []

        self.__exclude = excludeList
        self.setBlockList(blockList)
        self.editingFinished.connect(self.__editingFinished)
        self.hide()
        self.blockSignals(True)

    def keyPressEvent(self, evnt):
        if evnt.key() == QtCore.Qt.Key_Escape:
            self.blockSignals(True)
            self.setText("")
            self.hide()

        super(BlockCreator, self).keyPressEvent(evnt)

    def setBlockList(self, blockList):
        comp = QtWidgets.QCompleter(filter(lambda x: x not in self.__exclude, blockList))
        comp.popup().setStyleSheet("QListView { font-size : 13px; border: 1px solid #8B8B8B; color: #EDEDED; background-color: #222222; }")
        comp.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # This is available in Qt 5.2 and later
        if hasattr(comp, "setFilterMode"):
            comp.setFilterMode(QtCore.Qt.MatchContains)

        comp.setModelSorting(QtWidgets.QCompleter.CaseInsensitivelySortedModel)
        self.setCompleter(comp)

    def show(self, pos):
        self.setText("")
        self.blockSignals(False)
        self.move(pos)
        self.setFocus(QtCore.Qt.PopupFocusReason)
        super(BlockCreator, self).show()

    def __editingFinished(self):
        self.BlockCreatorEnd.emit(self.text())
        self.blockSignals(True)
        self.hide()
