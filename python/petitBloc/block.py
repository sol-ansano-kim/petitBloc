from . import component
from . import util
from . import core


class ParamBlock(component.Component):
    def __init__(self, name="", parent=None):
        super(ParamBlock, self).__init__(name=name, parent=parent)
        self.__params = []

    def run(self):
        for p in self.__params:
            prt = self.outputFromName(p.name())
            if prt is not None:
                prt.send(p.get())

    def addParam(self, typeClass=None, name=None, value=None):
        if name is None or not util.validateName(name):
            name = "param"

        all_names = map(lambda x: x.name(), self.__params)

        name = util.GetUniqueName(name, all_names)

        p = core.Parameter(name, typeClass=typeClass, value=value, parent=self)
        if p:
            self.__params.append(p)
            super(ParamBlock, self).addOutput(p.typeClass(), name=p.name())

        return p

    def removeParam(self, param):
        if param in self.__params:
            p = self.outputFromName(param.name())
            super(ParamBlock.removeOutput(p))
            self.__params.remove(param)
            return True

        return False

    def params(self):
        for p in self.__params:
            yield p

    def param(self, index):
        if index <= 0 or index > len(self.__params):
            return None

        return self.__params[index]

    def paramFromName(self, name):
        for p in self.__params:
            if p.name() == name:
                return p

        return None

    def addInput(self, typeClass, name=None):
        return None

    def addOutput(self, typeClass, name=None):
        return None

    def removeInput(self, inPort):
        return False

    def removeOutput(self, outPort):
        return False


class Block(component.Component):
    def __init__(self, name="", parent=None):
        super(Block, self).__init__(name=name, parent=parent)

    def run(self):
        # override this method
        pass

    def initialize(self):
        # override this method
        pass
