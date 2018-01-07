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
        self.__packets = []
        self.__is_connected = True

        srcPort.addOutput(self)
        dstPort.setInput(self)

        if srcPort.typeClass() != dstPort.typeClass():
            self.__need_to_cast = True

    def isConnected(self):
        return self.__is_connected

    def disconnect(self):
        self.__src.disconnectChain(self)
        self.__dst.disconnectChain(self)
        self.__src = None
        self.__dst = None
        for p in self.__packets:
            p.drop()

        self.__packets = []
        self.__is_connected = False

    def push(self, pack):
        # TODO : improve on case when packet is passed to other block
        pack.pickUp()

        # TODO : thread lock
        self.__packets.append(pack)
        # TODO : send packet to dst

    def pop(self):
        if not self.__src:
            return None

        if not self.__packets:
            if not self.__src.request():
                return None

        # TODO : suspend
        if not self.__packets:
            return None

        # TODO : thread lock
        return self.__packets.pop(0)
