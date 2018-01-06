from numbers import Number
import packet


class Port(object):
    In = 0
    Out = 1

    def __init__(self, typeClass, direction, name=None, parent=None):
        super(Port, self).__init__()
        self.__direction = direction
        self.__type_class = typeClass
        self.__parent = parent
        self.__out_chains = []
        self.__in_chain = None
        self.__name = name
        if name is None:
            if direction is Port.In:
                self.__name = "in"
            else:
                self.__name = "out"

    def name(self):
        return self.__name

    def match(self, port):
        if self.__type_class == port.typeClass():
            return True

        if issubclass(self.__type_class, Number) and issubclass(port.typeClass(), Number):
            return True

        return False

    def direction(self):
        return self.__direction

    def isInPort(self):
        return self.__direction is Port.In

    def isOutPort(self):
        return self.__direction is Port.Out

    def typeClass(self):
        return self.__type_class

    def addOutput(self, chain):
        if chain not in self.__out_chains:
            self.__out_chains.append(chain)

    def setInput(self, chain):
        if self.__in_chain:
            self.__in_chain.disconnect()

        self.__in_chain = chain

    def disconnectChain(self, chain):
        if self.__in_chain == chain:
            self.__in_chain = None
            return

        if chain in self.__out_chains:
            self.__out_chains.remove(chain)

    def send(self, value):
        if self.__direction is Port.In:
            return False

        if not self.__out_chains:
            return False

        pack = None
        if isinstance(value, self.__type_class):
            pack = packet.Packet(value)

        elif issubclass(self.__type_class, Number) and isinstance(value, Number):
            pack = packet.Packet(self.__type_class(value))

        if pack is None:
            return False

        for chain in self.__out_chains:
            chain.push(pack)

        return True

    def receive(self):
        if self.__in_chain is None:
            return None

        return self.__in_chain.pop()

    def request(self):
        if self.__parent is None:
            return False

        if self.__parent.isWaiting():
            ## TODO : do it on other thread
            self.__parent.run()

        return True


class InPort(Port):
    def __init__(self, typeClass, parent=None):
        super(InPort, self).__init__(typeClass, Port.In, parent=parent)


class OutPort(Port):
    def __init__(self, typeClass, parent=None):
        super(OutPort, self).__init__(typeClass, Port.Out, parent=parent)
