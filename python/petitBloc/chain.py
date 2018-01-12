from numbers import Number
from . import core
from . import packet
from . import processManager


class Chain(core.ChainBase):
    def __init__(self, srcPort, dstPort):
        super(Chain, self).__init__(srcPort, dstPort)
        self.__packets = None
        self.__is_activated = False

    def empty(self):
        if self.__packets is None:
            return True

        return self.__packets.empty()

    def disconnect(self):
        super(Chain, self).disconnect()

        if self.__packets is not None:
            while (not self.__packets.empty()):
                self.__packets.get().drop()

    def activate(self):
        if not self.__is_activated:
            self.__is_activated = True
            self.__packets = processManager.QueueManager.CreateQueue()

    def terminate(self):
        if self.__is_activated and self.__packets.empty():
            self.__packets = processManager.QueueManager.DeleteQueue(self.__packets)
            if self.__packets is None:
                self.__is_activated = False

    def send(self, pack):
        if self.dst() is None:
            return False

        pack.pickUp()

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
