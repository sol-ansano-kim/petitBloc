from numbers import Number
import copy


class PacketBase(object):
    def __init__(self, value=None):
        super(PacketBase, self).__init__()
        self.__value = value
        self.__type_class = value.__class__

    def __repr__(self):
        self.__str__()

    def __str__(self):
        return "Packet<'{}'>".format(self.__type_class.__name__)

    def typeClass(self):
        return self.__type_class

    def value(self):
        return copy.deepcopy(self.__value)

    def _del(self):
        del self.__value
        del self

    def pickUp(self):
        pass

    def drop(self):
        pass

    def refCount(self):
        return -1

    def isEOP(self):
        return False


class PortBase(object):
    def __init__(self, typeClass, name=None, parent=None):
        super(PortBase, self).__init__()
        self.__type_class = typeClass
        self.__parent = parent
        self.__name = name

    def name(self):
        return self.__name

    def parent(self):
        return self.__parent

    def match(self, port):
        if self.__type_class == port.typeClass():
            return True

        if issubclass(self.__type_class, Number) and issubclass(port.typeClass(), Number):
            return True

        return False

    def isConnected(self):
        return False

    def getChains(self):
        return []

    def typeClass(self):
        return self.__type_class

    def isInPort(self):
        return False

    def isOutPort(self):
        return False

    def activate(self):
        pass

    def terminate(self):
        pass


class ChainBase(object):
    def __new__(self, srcPort, dstPort):
        if not srcPort.isOutPort() or not dstPort.isInPort():
            return None

        if not dstPort.match(srcPort):
            return None

        return super(ChainBase, self).__new__(self, srcPort, dstPort)

    def __init__(self, srcPort, dstPort):
        super(ChainBase, self).__init__()
        self.__src = srcPort
        self.__dst = dstPort
        self.__need_to_cast = False

    def src(self):
        return self.__src

    def dst(self):
        return self.__dst

    def isConnected(self):
        return (self.__src is not None) and (self.__dst is not None)

    def empty(self):
        return True

    def disconnect(self):
        self.__src.disconnect(self)
        self.__dst.disconnect(self)
        self.__src = None
        self.__dst = None

    def activate(self):
        pass

    def terminate(self):
        pass

    def send(self, pack):
        return False

    def sendEOP(self):
        return False

    def receive(self, timeout=None):
        return None


class ComponentBase(object):
    Initialized = 0
    Active = 1
    Terminated = 2

    def __init__(self, name="", parent=None):
        self.__name = name
        self.__class_name = self.__class__.__name__
        self.__state = ComponentBase.Initialized
        self.__parent = parent

    def __str__(self):
        return "{}<'{}'>".format(self.__class_name, self.__name)

    def __repr__(self):
        return self.__str__()

    def name(self):
        return self.__name

    def hasSubnet(self):
        return False

    def getSchedule(self):
        return []

    def run(self):
        pass

    def initialize(self):
        pass

    def state(self):
        return self.__state

    def isWaiting(self):
        return self.__state is ComponentBase.Initialized

    def isWorking(self):
        return self.__state is ComponentBase.Active

    def isTerminated(self):
        return self.__state is ComponentBase.Terminated

    def activate(self):
        self.__state = ComponentBase.Active

    def terminate(self):
        self.__state = ComponentBase.Terminated

    def addInput(self, typeClass, name=None):
        return None

    def addOutput(self, typeClass, name=None):
        return None

    def outputs(self):
        yield None

    def inputs(self):
        yield None

    def output(self, index=0):
        return None

    def input(self, index=0):
        return None

    def upstream(self):
        return []
        
    def downstream(self):
        return []
