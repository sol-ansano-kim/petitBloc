from Qt import QtCore
from .. import box
from .. import chain
from .. import blockManager
from .. import workerManager
from . import uiUtil
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
        self.__logs = {"totalTime": 0, "execCount": 0, "avgTime": 0, "timeLogs": {}, "error": {}, "warn": {}, "debug": {}}

    def resetLogs(self):
        self.__logs = {"totalTime": 0, "execCount": 0, "avgTime": 0, "timeLogs": {}, "error": {}, "warn": {}, "debug": {}}
        workerManager.WorkerManager.ResetLog()

    def readLogs(self):
        self.__logs = {"totalTime": 0, "execCount": 0, "avgTime": 0, "timeLogs": {}, "error": {}, "warn": {}, "debug": {}}
        self.__logs["totalTime"] = workerManager.WorkerManager.TotalTime()
        self.__logs["execCount"] = workerManager.WorkerManager.ExecutionCount()
        self.__logs["avgTime"] = workerManager.WorkerManager.AverageTime()
        self.__logs["timeLogs"] = workerManager.WorkerManager.TimeLogs()
        self.__logs["error"] = workerManager.WorkerManager.ErrorLogs()
        self.__logs["warn"] = workerManager.WorkerManager.WarnLogs()
        self.__logs["debug"] = workerManager.WorkerManager.DebugLogs()

    def getState(self):
        return (self.__logs["execCount"], len(self.__logs["error"].keys()), self.__logs["totalTime"], self.__logs["avgTime"])

    def getLogs(self, path):
        return (self.__logs["timeLogs"].get(path, 0), self.__logs["debug"].get(path, []), self.__logs["warn"].get(path, []), self.__logs["error"].get(path, []))

    def box(self):
        return self.__box

    def createContext(self):
        return self.__box.createContext()

    def deleteContext(self):
        return self.__box.deleteContext()

    def findObjectClass(self, name):
        return self.__manager.findObjectClass(name)

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

    def blockTree(self):
        return self.__manager.blockTree()

    def config(self, name):
        return self.__manager.config(name)

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

    def addBlock(self, blockType, name=None):
        bc = self.__manager.block(blockType)
        if bc:
            try:
                bi = bc(name=name)
            except Exception as e:
                print("Warning : Could not create an instance of {}".format(blockType))
                return None

            self.__box.addBlock(bi)
            self.__blocs.append(bi)

            return bi

        return None

    def serialize(self):
        data = {"blocks": [], "connections": [], "proxyPorts": []}

        blocks = self.__box.getSchedule()
        boxies = []

        ## block data
        for b in blocks:
            if b == self.__box:
                continue

            if isinstance(b, box.Box):
                boxies.append(b)

            block_data = {}
            if isinstance(b, box.ProxyBlock):
                if b.parent() == self.__box:
                    continue

                block_data["preservered"] = True

            block_data["path"] = uiUtil.PopRootPath(b.path())
            block_data["type"] = b.type()

            params = {}
            for p in b.params(includeExtraParam=False):
                value = p.get()
                expr = p.getExpression() if p.hasExpression() else None
                params[p.name()] = {"value": value, "expression": expr}

            extra = {}
            for p in b.extraParams():
                value = p.get()
                expr = p.getExpression() if p.hasExpression() else None
                typeName = p.typeClass().__name__
                extra[p.name()] = {"value": value, "expression": expr, "type": typeName}

            if params:
                block_data["params"] = params

            if extra:
                block_data["extraParams"] = extra

            data["blocks"].append(block_data)

        ## proxy ports
        for b in boxies:
            in_data = []
            out_data = []
            box_data = {"path": uiUtil.PopRootPath(b.path()), "in": in_data, "out": out_data}
            data["proxyPorts"].append(box_data)

            for pn in sorted(b.inputProxies()):
                op = b.inputProxyOut(pn)
                if op is None:
                    continue

                in_data.append({"name": pn, "type": op.typeClass().__name__})

            for pn in sorted(b.outputProxies()):
                ip = b.outputProxyIn(pn)
                out_data.append({"name": pn, "type": ip.typeClass().__name__})

        ## connection data
        for b in blocks:
            for p in b.inputs():
                if not p.isConnected():
                    continue

                src_port = map(lambda x: x.src(), p.chains())[0]

                data["connections"].append({"path": uiUtil.PopRootPath(p.path()), "src": uiUtil.PopRootPath(src_port.path())})

        return data

    def run(self, perProcessCallback=None):
        schedule = self.__box.getSchedule()
        workerManager.WorkerManager.RunSchedule(schedule, perProcessCallback=perProcessCallback)
