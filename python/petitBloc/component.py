from . import port
from . import util
from . import core
import multiprocessing


class Component(core.ComponentBase):
    def __init__(self, name="", parent=None):
        super(Component, self).__init__(name=name, parent=parent)
        self.__inputs = []
        self.__outputs = []
        self.initialize()

    def getSchedule(self):
        return [self]

    def activate(self):
        super(Component, self).activate()
        for inp in self.__inputs:
            inp.activate()

        for out in self.__outputs:
            out.activate()

    def terminate(self):
        for out in self.__outputs:
            out.sendEOP()

        for inp in self.__inputs:
            inp.terminate()

        super(Component, self).terminate()

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
