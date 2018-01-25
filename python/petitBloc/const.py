import enum


RootBoxName = "scene"
InProxyBlock = "in"
OutProxyBlock = "out"


class LogLevel(enum.Enum):
    Debug = 0
    Warn = 1
    Error = 2
    NoLog = 3

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
