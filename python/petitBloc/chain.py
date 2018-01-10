import multiprocessing
from numbers import Number
from . import core
from . import packet


class Chain(core.ChainBase):
    def __init__(self, srcPort, dstPort):
        super(Chain, self).__init__(srcPort, dstPort)
        self.__packets = None
        self.__is_activated = False

        srcPort.connect(self)
        dstPort.connect(self)

        if srcPort.typeClass() != dstPort.typeClass():
            self.__need_to_cast = True

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
            self.__packets = multiprocessing.Queue()

    def terminate(self):
        if self.__is_activated:
            self.__is_activated = False
            self.__packets.close()
            del self.__packets
            self.__packets = None

    def send(self, pack):
        if self.dst() is None:
            return False

        # TODO : improve on case when packet is passed to other block
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

        return self.__packets.get(timeout=timeout)
