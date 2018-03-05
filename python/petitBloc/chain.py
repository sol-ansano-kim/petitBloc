from numbers import Number
from . import core
from . import packet
from . import workerManager


class Chain(core.ChainBase):
    def __init__(self, srcPort, dstPort):
        super(Chain, self).__init__(srcPort, dstPort)
        self.__packets = None

    def empty(self):
        if self.__packets is None:
            return True

        return self.__packets.empty()

    def clear(self):
        if self.__packets is not None:
            while (not self.__packets.empty()):
                self.__packets.get().drop()

            workerManager.WorkerManager.DeleteQueue(self.__packets)
            self.__packets = None

    def disconnect(self):
        super(Chain, self).disconnect()

        self.clear()

    def activate(self):
        if self.dst() is not None and self.__packets is None:
            self.__packets = workerManager.WorkerManager.CreateQueue()

    def terminate(self):
        self.clear()

    def send(self, pack):
        if self.dst() is None:
            return False

        if self.__packets is None:
            return False

        self.__packets.put(pack)

        return True

    def sendEOP(self):
        return self.send(packet.EndOfPacket)

    def receive(self, timeout=None):
        if self.src() is None:
            return packet.EndOfPacket

        if self.__packets is None:
            return packet.EndOfPacket

        p = self.__packets.get(timeout=timeout)
        if self.needToCast() and not p.isEOP():
            p = packet.CastedPacket(p, self.dst().typeClass())

        return p
