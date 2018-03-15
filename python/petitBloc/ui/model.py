from Qt import QtCore
from .. import box
from .. import chain
from .. import proxy
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

        for prx in self.__box.inputProxies():
            if not prx.isConnected():
                self.__box.removeInputProxy(prx)
                inputs.append(prx)

        return inputs

    def cleanUpOutputProxies(self):
        outputs = []

        for prx in self.__box.outputProxies():
            if not prx.isConnected():
                self.__box.removeOutputProxy(prx)
                outputs.append(prx)

        return outputs

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

        if srcPort.isProxy() or dstPort.isProxy():
            chn = proxy.ProxyChain(srcPort, dstPort)
        else:
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
                bi = bc()
                if name is not None:
                    bi.rename(name)
            except Exception as e:
                print("Warning : Could not create an instance of {}".format(blockType))
                print(e)
                return None

            self.__box.addBlock(bi)
            self.__blocs.append(bi)

            return bi

        return None

    def serialize(self, include=[], exclude=[]):
        data = {"blocks": [], "connections": [], "proxyPorts": []}

        blocks = []
        boxies = []
        box_path = self.__box.path()

        for b in self.__box.getSchedule():
            if b == self.__box:
                continue

            if include and b.path() not in include:
                continue

            if b.path() in exclude:
                continue

            blocks.append(b)

        if include:
            additional_blocks = []

            for b in blocks:
                if b == self.__box:
                    continue

                if not b.hasNetwork():
                    continue

                box_children = b.getSchedule()
                include += map(lambda x: x.path(), box_children)
                additional_blocks += box_children

            blocks += additional_blocks

        blocks = list(set(blocks))
        include = list(set(include))

        ## block data
        for b in blocks:
            if isinstance(b, box.Box):
                boxies.append(b)

            block_data = {}
            if b.isProxy():
                if b.parent() == self.__box:
                    continue

                block_data["preservered"] = True

            block_data["path"] = uiUtil.PopRootPath(b.path(), box_path)
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
            box_data = {"path": uiUtil.PopRootPath(b.path(), box_path), "in": in_data, "out": out_data}
            data["proxyPorts"].append(box_data)

            for pn in sorted(b.inputProxies()):
                in_data.append({"name": pn.name(), "type": pn.typeClass().__name__})

            for pn in sorted(b.outputProxies()):
                out_data.append({"name": pn.name(), "type": pn.typeClass().__name__})

        ## connection data
        for b in blocks:
            if b.isProxy():
                inputs = map(lambda x: x.inPort(), b.proxies())
            else:
                inputs = b.inputs()

            for p in inputs:
                if not p.isConnected():
                    continue

                src_path = None
                dst_path = None
                src_port = map(lambda x: x.src(), p.chains())[0]

                src_parent = src_port.parent()
                if src_parent.isProxy():
                    src_parent = src_parent.parent()

                if include and src_parent.path() not in include:
                    continue

                if src_port.parent().path() in exclude:
                    continue

                if src_port.isProxy():
                    src_path = src_port.parent().path()
                else:
                    src_path = src_port.path()

                if p.isProxy():
                    dst_path = p.parent().path()
                else:
                    dst_path = p.path()

                data["connections"].append({"path": uiUtil.PopRootPath(dst_path, box_path), "src": uiUtil.PopRootPath(src_path, box_path)})

        return data

    def run(self, manager=None):
        callback = None
        schedule = self.__box.getSchedule()

        if manager is not None:
            manager.reset()
            manager.setCount(len(schedule))
            callback = manager.increase

        workerManager.WorkerManager.RunSchedule(schedule, perProcessCallback=callback)
