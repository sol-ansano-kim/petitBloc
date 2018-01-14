from .. import box
from .. import blockManager


class BoxModel(object):
    def __init__(self, name):
        super(BoxModel, self).__init__()
        self.__box = box.Box(name)
        self.__blockManager = blockManager.BlockManager()

    def blockNames(self):
        return self.__blockManager.blockNames()

    def addBlock(self, name):
        bloc_cls = self.__blockManager.block(name)
        if bloc_cls is None:
            return None

        bloc = bloc_cls(name)
        if not self.__box.addBlock(bloc):
            return None

        return BlockModel(bloc)


class PortModel(object):
    def __init__(self, port, parent=None):
        super(PortModel, self).__init__()
        self.__port = port
        self.__parent = parent

    def name(self):
        return self.__port.name()

    def type(self):
        return self.__port.typeClass()

    def isInPort(self):
        return self.__port.isInPort()

    def isOutPort(self):
        return self.__port.isOutPort()


class BlockModel(object):
    def __init__(self, bloc):
        super(BlockModel, self).__init__()
        self.__block = bloc

    def name(self):
        return self.__block.name()

    def inputs(self):
        inputs = []

        for inp in self.__block.inputs():
            inputs.append(PortModel(inp))

        return inputs

    def outputs(self):
        outputs = []

        for oup in self.__block.outputs():
            outputs.append(PortModel(oup))

        return outputs

    def type(self):
        return self.__block.__class__.__name__

