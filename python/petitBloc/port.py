from numbers import Number
from . import packet
from . import core
from . import workerManager
import copy


class InPort(core.PortBase):
    def __init__(self, typeClass, name=None, parent=None):
        super(InPort, self).__init__(typeClass, name=name, parent=parent)
        self.__in_chain = None
        self.__values = []
        self.__value_queue = None

    def packetHistory(self):
        return copy.copy(self.__values)

    def isInPort(self):
        return True

    def isConnected(self):
        return self.__in_chain is not None

    def chains(self):
        if self.__in_chain is not None:
            yield self.__in_chain

    def connect(self, chain):
        if self.__in_chain:
            self.__in_chain.disconnect()

        self.__in_chain = chain

    def disconnect(self, chain):
        if self.__in_chain == chain:
            self.__in_chain = None

    def receive(self):
        if self.__in_chain is None:
            return packet.EndOfPacket

        p = self.__in_chain.receive()
        if self.__value_queue is not None and not p.isEOP():
            self.__value_queue.put(p.value())

        return p

    def activate(self):
        self.__values = []

        if self.__value_queue is not None:
            workerManager.WorkerManager.DeleteQueue(self.__value_queue)
            self.__value_queue = None

        self.__value_queue = workerManager.WorkerManager.CreateQueue()

        if self.__in_chain:
            self.__in_chain.activate()

    def terminate(self):
        if self.__value_queue is not None:
            while (not self.__value_queue.empty()):
                self.__values.append(self.__value_queue.get())

            workerManager.WorkerManager.DeleteQueue(self.__value_queue)
            self.__value_queue = None

        if self.__in_chain:
            self.__in_chain.terminate()


class OutPort(core.PortBase):
    def __init__(self, typeClass, name=None, parent=None):
        super(OutPort, self).__init__(typeClass, name=name, parent=parent)
        self.__out_chains = []
        self.__values = []
        self.__value_queue = None

    def packetHistory(self):
        return copy.copy(self.__values)

    def isOutPort(self):
        return True

    def isConnected(self):
        return len(self.__out_chains) > 0

    def chains(self):
        for c in self.__out_chains:
            yield c

    def connect(self, chain):
        if chain not in self.__out_chains:
            self.__out_chains.append(chain)

    def disconnect(self, chain):
        if chain in self.__out_chains:
            self.__out_chains.remove(chain)

    def terminate(self):
        if self.__value_queue is not None:
            while (not self.__value_queue.empty()):
                self.__values.append(self.__value_queue.get())

            workerManager.WorkerManager.DeleteQueue(self.__value_queue)
            self.__value_queue = None

        for chain in self.__out_chains:
            chain.sendEOP()

    def send(self, value):
        if not self.__out_chains:
            return False

        pack = None
        if isinstance(value, self.typeClass()):
            pack = packet.Packet(value)

        elif issubclass(self.typeClass(), Number) and isinstance(value, Number):
            pack = packet.Packet(self.typeClass()(value))

        elif issubclass(self.typeClass(), basestring) and isinstance(value, basestring):
            pack = packet.Packet(self.typeClass()(value))

        if pack is None:
            return False

        if self.__value_queue is not None and not pack.isEOP():
            self.__value_queue.put(pack.value())

        for chain in self.__out_chains:
            chain.send(pack)

        return True

    def activate(self):
        self.__values = []

        if self.__value_queue is not None:
            workerManager.WorkerManager.DeleteQueue(self.__value_queue)
            self.__value_queue = None

        self.__value_queue = workerManager.WorkerManager.CreateQueue()

        for out in self.__out_chains:
            out.activate()
