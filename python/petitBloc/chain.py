import multiprocessing
from numbers import Number
from . import packet


class Chain(object):
    def __new__(self, srcPort, dstPort):
        if not srcPort.isOutPort() or not dstPort.isInPort():
            return None

        if not dstPort.match(srcPort):
            return None

        return super(Chain, self).__new__(self, srcPort, dstPort)

    def __init__(self, srcPort, dstPort):
        self.__src = srcPort
        self.__dst = dstPort
        self.__need_to_cast = False
        self.__packets = None
        self.__is_activated = False

        srcPort.connect(self)
        dstPort.connect(self)

        if srcPort.typeClass() != dstPort.typeClass():
            self.__need_to_cast = True

    def src(self):
        return self.__src

    def dst(self):
        return self.__dst

    def isConnected(self):
        return (self.__src is not None) and (self.__dst is not None)

    def empty(self):
        if self.__packets is None:
            return True

        return self.__packets.empty()

    def disconnect(self):
        self.__src.disconnect(self)
        self.__dst.disconnect(self)
        self.__src = None
        self.__dst = None

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
        if self.__dst is None:
            return False

        # TODO : improve on case when packet is passed to other block
        pack.pickUp()

        self.__packets.put(pack)
        return True

    def sendEOP(self):
        self.send(packet.EndOfPacket)

    def receive(self, timeout=None):
        if self.__src is None:
            return packet.EndOfPacket

        if self.__packets is None:
            return packet.EndOfPacket

        return self.__packets.get(timeout=timeout)
