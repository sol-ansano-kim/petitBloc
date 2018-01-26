from numbers import Number
from . import core


class Parameter(core.ParameterBase):
    def __new__(self, name, typeClass=None, value=None, parent=None):
        if value is None and typeClass is None:
            return None

        if value is not None:
            if not isinstance(value, Number) and not isinstance(value, basestring):
                return None

            if typeClass is not None:
                if not isinstance(value, typeClass):
                    if (not issubclass(typeClass, Number) or not isinstance(value, Number)) and (not issubclass(typeClass, basestring) or not isinstance(value, basestring)):
                        return None

        else:
            if not issubclass(typeClass, Number) and not issubclass(typeClass, basestring):
                return None

        return super(Parameter, self).__new__(self, name, typeClass=typeClass, value=value, parent=parent)

    def __init__(self, name, typeClass=None, value=None, parent=None):
        super(Parameter, self).__init__(name, typeClass=typeClass, value=value, parent=parent)
        if value is None:
            self.__value = typeClass()
            self.__type_class = typeClass

        elif typeClass is None:
            self.__value = value
            self.__type_class = value.__class__

        else:
            self.__value = typeClass(value)
            self.__type_class = typeClass

    def __str__(self):
        return "Parameter<'{}'>".format(self.name())

    def typeClass(self):
        return self.__type_class

    def get(self):
        return self.__value

    def set(self, value):
        if isinstance(value, self.__type_class):
            self.__value = value
            return True

        if isinstance(value, Number) and issubclass(self.__type_class, Number):
            self.__value = value
            return True

        if isinstance(value, basestring) and issubclass(self.__type_class, basestring):
            self.__value = value
            return True

        return False

