from . import port
from . import util
import multiprocessing


class Component(object):
    Initialized = 0
    Active = 1
    Terminated = 2

    def __init__(self, name="", parent=None):
        self.__name = name
        self.__class_name = self.__class__.__name__
        self.__inputs = []
        self.__outputs = []
        self.__state = multiprocessing.Value("i", Component.Initialized)
        self.__parent = parent
        self.initialize()

    def __str__(self):
        return "{}<'{}'>".format(self.__class_name, self.__name)

    def __repr__(self):
        return self.__str__()

    def name(self):
        return self.__name

    def run(self):
        pass

    def initialize(self):
        pass

    def state(self):
        return self.__state.value

    def isWaiting(self):
        return self.__state.value is Component.Initialized

    def isWorking(self):
        return self.__state.value is Component.Active

    def isTerminated(self):
        return self.__state.value is Component.Terminated

    def activate(self):
        self.__state.value = Component.Active

    def terminate(self):
        for out in self.__outputs:
            out.sendEOP()

        self.__state.value = Component.Terminated

    def addInput(self, typeClass, name=None):
        if name is None or not util.validateName(name):
            name = "input"

        all_names = map(lambda x: x.name(), self.__inputs)

        name = util.GetUniqueName(name, all_names)

        p = port.InPort(typeClass, name=name, parent=self)
        self.__inputs.append(p)

        return p

    def addOutput(self, typeClass, name=None):
        if name is None or not util.validateName(name):
            name = "output"

        all_names = map(lambda x: x.name(), self.__outputs)    

        name = util.GetUniqueName(name, all_names)

        p = port.OutPort(typeClass, name=name, parent=self)
        self.__outputs.append(p)    

        return p

    def outputs(self):
        for p in self.__outputs:
            yield p

    def inputs(self):
        for p in self.__inputs:
            yield p

    def output(self, index=0):
        if index >= len(self.__outputs) or index < 0:
            return None

        return self.__outputs[index]

    def input(self, index=0):
        if index >= len(self.__inputs) or index < 0:
            return None

        return self.__inputs[index]

    def upstream(self):
        upstreams = []
        for inp in self.__inputs:
            for chn in inp.getChains():
                src = chn.src()
                up = src.parent()
                if up:
                    upstreams.append(up)

        return upstreams
        
    def downstream(self):
        downstreams = []
        for oup in self.__outputs:
            for chn in oup.getChains():
                dst = chn.dst()
                down = dst.parent()
                if down:
                    downstreams.append(down)

        return downstreams


class Block(Component):
    def __init__(self, name="", parent=None):
        super(Block, self).__init__(name=name, parent=parent)

    def run(self):
        # override this method
        self.terminate()

    def initialize(self):
        # override this method
        pass
