import copy
from . import core


class EndOfPacketObject(core.PacketBase):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(EndOfPacketObject, cls).__new__(cls)

        return cls.__instance

    def __init__(self):
        super(EndOfPacketObject, self).__init__(value=-1)

    def __repr__(self):
        self.__str__()

    def __str__(self):
        return "Packet<'EndOfPacket'>"

    def pickUp(self):
        pass

    def drop(self):
        pass

    def value(self):
        return None

    def typeClass(self):
        return None

    def refCount(self):
        return -1

    def isEOP(self):
        return True


EndOfPacket = EndOfPacketObject()


class Packet(core.PacketBase):
    def __init__(self, value=None):
        super(Packet, self).__init__(value=value)
        self.__ref_count = 0

    def refCount(self):
        return self.__ref_count

    def setRefCount(self, v):
        self.__ref_count = v

    def pickUp(self):
        self.__ref_count += 1

    def drop(self):
        self.__ref_count -= 1

        if self.__ref_count <= 0:
            self._del()
            return True

        return False


class CastedPacket(core.PacketBase):
    def __init__(self, packet, typeClass=None):
        if typeClass is not None:
            super(CastedPacket, self).__init__(value=typeClass(packet.value()))
        else:
            super(CastedPacket, self).__init__(value=packet.value())

        self.pickUp = packet.pickUp
        self.drop = packet.drop
