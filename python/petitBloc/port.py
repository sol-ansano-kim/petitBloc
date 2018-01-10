from numbers import Number
from . import packet
from . import core


class InPort(core.PortBase):
    def __init__(self, typeClass, name=None, parent=None):
        super(InPort, self).__init__(typeClass, name=name, parent=parent)
        self.__in_chain = None

    def isInPort(self):
        return True

    def isConnected(self):
        return self.__in_chain is not None

    def getChains(self):
        return [self.__in_chain] if self.__in_chain is not None else []

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

        return self.__in_chain.receive()

    def activate(self):
        if self.__in_chain:
            self.__in_chain.activate()

    def terminate(self):
        if self.__in_chain:
            self.__in_chain.terminate()


class OutPort(core.PortBase):
    def __init__(self, typeClass, name=None, parent=None):
        super(OutPort, self).__init__(typeClass, name=name, parent=parent)
        self.__out_chains = []

    def isOutPort(self):
        return True

    def isConnected(self):
        return len(self.__out_chains) > 0

    def getChains(self):
        return self.__out_chains

    def connect(self, chain):
        if chain not in self.__out_chains:
            self.__out_chains.append(chain)

    def disconnect(self, chain):
        if chain in self.__out_chains:
            self.__out_chains.remove(chain)

    def sendEOP(self):
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

        if pack is None:
            return False

        for chain in self.__out_chains:
            chain.send(pack)

        return True

    def activate(self):
        for out in self.__out_chains:
            out.activate()
