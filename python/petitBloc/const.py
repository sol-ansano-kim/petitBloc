import enum


RootBoxName = "scene"
InProxyBlock = "in"
OutProxyBlock = "out"
BlockResultPortName = "success"


class LogLevel(enum.Enum):
    NoLog = 0
    Error = 1
    Warn = 2
    Debug = 3

    def __gt__(self, b):
        return self._value_ > b._value_

    def __ge__(self, b):
        return self._value_ >= b._value_

    def __lt__(self, b):
        return self._value_ < b._value_

    def __le__(self, b):
        return self._value_ <= b._value_

    def __eq__(self, b):
        return self._value_ == b._value_
