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
        self.__packets = multiprocessing.Queue()

        srcPort.connect(self)
        dstPort.connect(self)

        if srcPort.typeClass() != dstPort.typeClass():
            self.__need_to_cast = True

    def closed(self):
        return self.__packets._closed

    def empty(self):
        return self.__packets.empty()

    def disconnect(self):
        self.__src.disconnect(self)
        self.__dst.disconnect(self)
        self.__src = None
        self.__dst = None

        while (not self.__packets.empty()):
            self.__packets.get().drop()

        self.__packets.close()

    def send(self, pack):
        if self.closed():
            return False

        # TODO : improve on case when packet is passed to other block
        pack.pickUp()

        self.__packets.put(pack)
        return True

    def receive(self):
        if self.closed():
            return None

        return self.__packets.get()
