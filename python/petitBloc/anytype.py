from . import core


class AnyType(core.Any):
    def __init__(self, value):
        super(AnyType, self).__init__(value)
