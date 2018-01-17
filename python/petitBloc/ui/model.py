from Qt import QtCore
from .. import box
from .. import blockManager
from .. import workerManager
import copy


class BoxModel(QtCore.QObject):
    BlockAdded = QtCore.Signal(str)
    BlockRemoved = QtCore.Signal(str)

    def __init__(self, name):
        super(BoxModel, self).__init__()
        self.__manager = blockManager.BlockManager()
        self.__name = name
        self.__box = box.Box(name)
        self.__blocs = []

    def blockClassNames(self):
        return self.__manager.blockNames()

    def connect(self, srcNode, srcPort, dstNode, dstPort):
        src_node = self.block(srcNode)
        if src_node is None:
            raise Exception, "Failed to find the srcNode : {}".format(srcNode)

        dst_node = self.block(dstNode)
        if dst_node is None:
            raise Exception, "Failed to find the dstNode : {}".format(dstNode)

        src_port = src_node.output(srcPort)
        if src_port is None:
            raise Exception, "Failed to find the srcPort : {}.{}".format(srcNode, srcPort)

        dst_port = dst_node.input(dstPort)
        if dst_port is None:
            raise Exception, "Failed to find the dstPort : {}.{}".format(dstNode, dstPort)

        res = self.__box.connect(src_port, dst_port)
        if not res:
            raise Exception, "Failed to connect ports : {}.{} > {}.{}".format(srcNode, srcPort, dstNode, dstPort)

    def disconnect(self, srcNode, srcPort, dstNode, dstPort):
        src_node = self.block(srcNode)
        if src_node is None:
            raise Exception, "Failed to find the srcNode : {}".format(srcNode)

        dst_node = self.block(dstNode)
        if dst_node is None:
            raise Exception, "Failed to find the dstNode : {}".format(dstNode)

        src_port = src_node.output(srcPort)
        if src_port is None:
            raise Exception, "Failed to find the srcPort : {}.{}".format(srcNode, srcPort)

        dst_port = dst_node.input(dstPort)
        if dst_port is None:
            raise Exception, "Failed to find the dstPort : {}.{}".format(dstNode, dstPort)

        if self.__box.isConnected(src_port, dst_port):
            if not self.__box.disconnect(src_port, dst_port):
                raise Exception, "Failed to disconnect ports : {}.{} > {}.{}".format(srcNode, srcPort, dstNode, dstPort)

    def block(self, name):
        for b in self.__box.blocks():
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
            self.__blocs.append(bi)

            return bi

        return None

    def run(self):
        schedule = self.__box.getSchedule()
        workerManager.WorkerManager.RunSchedule(schedule)
