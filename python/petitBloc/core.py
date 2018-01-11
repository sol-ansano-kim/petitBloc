from numbers import Number
import copy


class Parameter(object):
    def __new__(self, name, typeClass=None, value=None):
        if value is None and typeClass is None:
            return None

        if value is not None:
            if not isinstance(value, Number) and not isinstance(value, basestring):
                return None

            if typeClass is not None:
                if not isinstance(value, typeClass):
                    if (not issubclass(typeClass, Number) or not isinstance(value, Number)) and (not issubclass(typeClass, basestring) or not isinstance(value, basestring)):
                        return None

        else:
            if not issubclass(typeClass, Number) and not issubclass(typeClass, basestring):
                return None

        return super(Parameter, self).__new__(self, name, typeClass=typeClass, value=value)

    def __init__(self, name, typeClass=None, value=None):
        super(Parameter, self).__init__()
        self.__name = name
        if value is None:
            self.__value = typeClass()
            self.__type_class = typeClass

        elif typeClass is None:
            self.__value = value
            self.__type_class = value.__class__

        else:
            self.__value = typeClass(value)
            self.__type_class = typeClass

    def __str__(self):
        return "Parameter<'{}'>".format(self.__name)

    def __repr__(self):
        return self.__str__()

    def name(self):
        return self.__name

    def typeClass(self):
        return self.__type_class

    def get(self):
        return self.__value

    def set(self, value):
        if isinstance(value, self.__type_class):
            self.__value = value
            return True

        if isinstance(value, Number) and issubclass(self.__type_class, Number):
            self.__value = value
            return True

        if isinstance(value, basestring) and issubclass(self.__type_class, basestring):
            self.__value = value
            return True

        return False


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
        for i in range(0):
            yield i

    def send(self):
        return False

    def receive(self):
        return None

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

    def activate(self):
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

    def needToCast(self):
        return self.__need_to_cast


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

    def parent(self):
        return self.__parent

    def setParent(self, parent):
        self.__parent = parent

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

    def removeInput(self, inPort):
        return False

    def removeOutput(self, outPort):
        return False

    def addOutput(self, typeClass, name=None):
        return None

    def outputs(self):
        for i in range(0):
            yield i

    def outputFromName(self, name):
        return None

    def inputFromName(self, name):
        return None

    def inputs(self):
        for i in range(0):
            yield i

    def output(self, index=0):
        return None

    def input(self, index=0):
        return None

    def upstream(self):
        return []
        
    def downstream(self):
        return []