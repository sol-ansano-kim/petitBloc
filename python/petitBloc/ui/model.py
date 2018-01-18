from Qt import QtCore
from .. import box
from .. import blockManager
from .. import workerManager
import copy


class BoxModel(QtCore.QObject):
    def __init__(self, name="", boxObject=None):
        super(BoxModel, self).__init__()
        if not name and not boxObject:
            raise Exception, "Failed to create BoxModel. Specify the name for a new box or a box object"

        if boxObject is not None:
            self.__box = boxObject
            self.__name = boxObject.name()
        else:
            self.__name = name
            self.__box = box.Box(name)

        self.__manager = blockManager.BlockManager()
        self.__blocs = []

    def blockClassNames(self):
        return self.__manager.blockNames()

    def connect(self, srcBloc, srcPort, dstBloc, dstPort):
        src_bloc = self.block(srcBloc)
        if src_bloc is None:
            raise Exception, "Failed to find the srcBloc : {}".format(srcBloc)

        dst_bloc = self.block(dstBloc)
        if dst_bloc is None:
            raise Exception, "Failed to find the dstBloc : {}".format(dstBloc)

        src_port = src_bloc.output(srcPort)
        if src_port is None:
            raise Exception, "Failed to find the srcPort : {}.{}".format(srcBloc, srcPort)

        dst_port = dst_bloc.input(dstPort)
        if dst_port is None:
            raise Exception, "Failed to find the dstPort : {}.{}".format(dstBloc, dstPort)

        res = self.__box.connect(src_port, dst_port)
        if not res:
            raise Exception, "Failed to connect ports : {}.{} > {}.{}".format(srcBloc, srcPort, dstBloc, dstPort)

    def disconnect(self, srcBloc, srcPort, dstBloc, dstPort):
        src_bloc = self.block(srcBloc)
        if src_bloc is None:
            raise Exception, "Failed to find the srcBloc : {}".format(srcBloc)

        dst_bloc = self.block(dstBloc)
        if dst_bloc is None:
            raise Exception, "Failed to find the dstBloc : {}".format(dstBloc)

        src_port = src_bloc.output(srcPort)
        if src_port is None:
            raise Exception, "Failed to find the srcPort : {}.{}".format(srcBloc, srcPort)

        dst_port = dst_bloc.input(dstPort)
        if dst_port is None:
            raise Exception, "Failed to find the dstPort : {}.{}".format(dstBloc, dstPort)

        if self.__box.isConnected(src_port, dst_port):
            if not self.__box.disconnect(src_port, dst_port):
                raise Exception, "Failed to disconnect ports : {}.{} > {}.{}".format(srcBloc, srcPort, dstBloc, dstPort)

    def deleteNode(self, nodeName):
        bloc = self.block(nodeName)
        if bloc is None:
            raise Exception, "Failed to find the block : {}".format(nodeName)

        if not self.__box.deleteBlock(bloc):
            raise Exception, "Failed to delete the block : {}".format(nodeName)

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

    def run(self, perProcessCallback=None):
        schedule = self.__box.getSchedule()
        workerManager.WorkerManager.RunSchedule(schedule, perProcessCallback=perProcessCallback)
