from . import port
from . import util
from . import core


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
            out.terminate()

        for inp in self.__inputs:
            inp.terminate()

        super(Component, self).terminate()

    def addInput(self, typeClass, name=None):
        if name is None or not util.validateName(name):
            name = "input"

        all_names = map(lambda x: x.name(), self.__inputs + self.__outputs)

        name = util.GetUniqueName(name, all_names)

        p = port.InPort(typeClass, name=name, parent=self)
        self.__inputs.append(p)

        return p

    def addOutput(self, typeClass, name=None):
        if name is None or not util.validateName(name):
            name = "output"

        all_names = map(lambda x: x.name(), self.__inputs + self.__outputs)

        name = util.GetUniqueName(name, all_names)

        p = port.OutPort(typeClass, name=name, parent=self)
        self.__outputs.append(p)    

        return p

    def removeInput(self, inPort):
        if inPort in self.__inputs:
            self.__inputs.remove(inPort)
            return True

        return False

    def removeOutput(self, outPort):
        if outPort in self.__outputs:
            self.__outputs.remove(outPort)
            return True

        return False

    def outputs(self):
        for p in self.__outputs:
            yield p

    def inputs(self):
        for p in self.__inputs:
            yield p

    def output(self, index_or_name):
        if isinstance(index_or_name, int):
            if index_or_name >= len(self.__outputs) or index_or_name < 0:
                return None

            return self.__outputs[index_or_name]

        if isinstance(index_or_name, basestring):
            for p in self.__outputs:
                if p.name() == index_or_name:
                    return p

        return None

    def input(self, index_or_name):
        if isinstance(index_or_name, int):
            if index_or_name >= len(self.__inputs) or index_or_name < 0:
                return None

            return self.__inputs[index_or_name]

        if isinstance(index_or_name, basestring):
            for p in self.__inputs:
                if p.name() == index_or_name:
                    return p

        return None

    def upstream(self):
        upstreams = []
        for inp in self.__inputs:
            for chn in inp.chains():
                src = chn.src()
                if src is None:
                    continue

                up = src.parent()
                if isinstance(up, core.Proxy):
                    continue

                if up:
                    upstreams.append(up)

        return upstreams
        
    def downstream(self):
        downstreams = []
        for oup in self.__outputs:
            for chn in oup.chains():
                dst = chn.dst()
                if dst is None:
                    continue

                down = dst.parent()
                if dst is None:
                    continue

                if isinstance(down, core.Proxy):
                    continue

                if down:
                    downstreams.append(down)

        return downstreams
