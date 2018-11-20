from .core import Any


class AnyType(Any):
    def __init__(self, value):
        super(AnyType, self).__init__(value)
