from Qt import QtCore
from .. import box
from .. import chain
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

    def box(self):
        return self.__box

    def cleanUpInputProxies(self):
        inputs = []
        outputs = []

        for proxy in self.__box.inputProxies():
            inp = self.__box.inputProxyIn(proxy)
            outp = self.__box.inputProxyOut(proxy)
            if not inp.isConnected() and not outp.isConnected():
                self.__box.removeInputProxy(proxy)
                inputs.append(inp.name())
                outputs.append(outp.name())

        return (inputs, outputs)

    def cleanUpOutputProxies(self):
        inputs = []
        outputs = []

        for proxy in self.__box.outputProxies():
            inp = self.__box.outputProxyIn(proxy)
            outp = self.__box.outputProxyOut(proxy)
            if not inp.isConnected() and not outp.isConnected():
                self.__box.removeOutputProxy(proxy)
                inputs.append(inp.name())
                outputs.append(outp.name())

        return (inputs, outputs)

    def addInputProxy(self, typeClass, name):
        return self.__box.addInputProxy(typeClass, name)

    def addOutputProxy(self, typeClass, name):
        return self.__box.addOutputProxy(typeClass, name)

    def removeInputProxy(self, port):
        if not self.__box.removeInputProxyPort(port):
            raise Exception, "Failed to remote to inProxy : {}".format(port.name())

    def removeOutputProxy(self, port):
        if not self.__box.removeOutputProxyPort(port):
            raise Exception, "Failed to remote to outProxy : {}".format(port.name())

    def inProxyBlock(self):
        return self.__box.inProxyBlock()

    def outProxyBlock(self):
        return self.__box.outProxyBlock()

    def blockClassNames(self):
        return self.__manager.blockNames()

    def connect(self, srcPort, dstPort):
        srcs = map(lambda x: x, dstPort.chains())

        if srcs:
            if srcs[0].src() == srcPort:
                return

        chn = chain.Chain(srcPort, dstPort)

        if chn is None:
            raise Exception, "Failed to connect {} to {}".format(srcPort.path(), dstPort.path())

    def disconnect(self, srcPort, dstPort):
        for c in dstPort.chains():
            c.disconnect()

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
