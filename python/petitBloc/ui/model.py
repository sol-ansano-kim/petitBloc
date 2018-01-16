from Qt import QtCore
from .. import box
from .. import blockManager
import copy


class BoxModel(QtCore.QObject):
    BlockAdded = QtCore.Signal(str)
    BlockRemoved = QtCore.Signal(str)

    def __init__(self, name):
        super(BoxModel, self).__init__()
        self.__manager = blockManager.BlockManager()
        self.__name = name
        self.__box = box.Box(name)
        self.__blocs = {}

    def blockClassNames(self):
        return self.__manager.blockNames()

    def block(self, name):
        for b in self.__box.blocks:
            if b.name() == name:
                return b

        return None

    def addBlock(self, name):
        bc = self.__manager.block(name)
        if bc:
            try:
                bi = bc()
            except Exception as e:
                return None

            self.__box.addBlock(bi)
            self.__blocs[bi.name()] = bi

            return bi

        return None
