from . import port
from . import util
from . import core
from . import workerManager
from . import parameter


class Component(core.ComponentBase):
    def __init__(self, name="", parent=None):
        super(Component, self).__init__(name=name, parent=parent)
        self.__inputs = []
        self.__outputs = []
        self.__params = []
        self.__extraParams = []
        self.initialize()

    def debug(self, message):
        workerManager.WorkerManager.Debug(self.path(), message)

    def warn(self, message):
        workerManager.WorkerManager.Warn(self.path(), message)

    def error(self, message):
        workerManager.WorkerManager.Error(self.path(), message)

    def getSchedule(self):
        return [self]

    def activate(self):
        super(Component, self).activate()
        for inp in self.__inputs:
            inp.activate()

        for out in self.__outputs:
            out.activate()

        for p in self.__params:
            p.activate()

    def terminate(self, success=True):
        for out in self.__outputs:
            out.terminate()

        for inp in self.__inputs:
            inp.terminate()

        for p in self.__params:
            p.terminate()

        super(Component, self).terminate(success=success)

    def clear(self):
        for out in self.__outputs:
            out.clear()

        for inp in self.__inputs:
            inp.clear()

        for p in self.__params:
            p.terminate()

    def addInput(self, typeClass, name=None):
        if name is None or not util.ValidateName(name):
            name = "input"

        all_names = map(lambda x: x.name(), self.__inputs + self.__outputs)

        name = util.GetUniqueName(name, all_names)

        p = port.InPort(typeClass, name=name, parent=self)
        self.__inputs.append(p)

        return p

    def addOutput(self, typeClass, name=None):
        if name is None or not util.ValidateName(name):
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

    def hasConnection(self, port):
        for p in self.__inputs:
            for c in p.chains():
                if c.dst() == port:
                    return True

        for p in self.__outputs:
            for c in p.chains():
                if c.src() == port:
                    return True

        return False

    def upstream(self, includeProxy=False):
        upstreams = []
        for inp in self.__inputs:
            for chn in inp.chains():
                src = chn.src()
                if src is None:
                    continue

                up = src.parent()
                if not includeProxy and up.isProxy():
                    continue

                if up:
                    upstreams.append(up)

        return upstreams
        
    def downstream(self, includeProxy=False):
        downstreams = []
        for oup in self.__outputs:
            for chn in oup.chains():
                dst = chn.dst()
                if dst is None:
                    continue

                down = dst.parent()
                if dst is None:
                    continue

                if not includeProxy and down.isProxy():
                    continue

                if down:
                    downstreams.append(down)

        return downstreams

    def removeParam(self, name_or_param):
        if isinstance(name_or_param, core.ParameterBase):
            if name_or_param in self.__params:
                self.__params.remove(name_or_param)
                if name_or_param in self.__extraParams:
                    self.__extraParams.remove(name_or_param)

                return True

            return False

        if isinstance(name_or_param, basestring):
            p = self.param(name_or_param)
            if p:
                self.__params.remove(p)
                if p in self.__extraParams:
                    self.__extraParams.remove(p)

                return True

        return False

    def addParam(self, typeClass=None, name=None, value=None):
        if name is None or not util.ValidateName(name):
            name = "param"

        all_names = map(lambda x: x.name(), self.__params)

        name = util.GetUniqueName(name, all_names)

        p = parameter.Parameter(name, typeClass=typeClass, value=value, parent=self)
        if p:
            self.__params.append(p)

        return p

    def addEnumParam(self, name, valueList, value=None):
        if name is None or not util.ValidateName(name):
            name = "param"

        all_names = map(lambda x: x.name(), self.__params)

        name = util.GetUniqueName(name, all_names)

        p = parameter.EnumParameter(name, valueList, value=value, parent=self)
        if p:
            self.__params.append(p)

        return p

    def params(self, includeExtraParam=True):
        for p in self.__params:
            if not includeExtraParam and p in self.__extraParams:
                continue

            yield p

    def addExtraParam(self, typeClass=None, name=None, value=None):
        p = self.addParam(typeClass=typeClass, name=name, value=value)
        if p is not None:
            self.__extraParams.append(p)
            return p

        return None

    def extraParams(self):
        for p in self.__extraParams:
            yield p

    def param(self, index_or_name):
        if isinstance(index_or_name, int):
            if index_or_name < 0 or index_or_name >= len(self.__params):
                return None

            return self.__params[index_or_name]

        if isinstance(index_or_name, basestring):
            for p in self.__params:
                if p.name() == index_or_name:
                    return p

        return None
