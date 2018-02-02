import os
import re
from numbers import Number
from . import core


ReContextParam = re.compile("[$][a-zA-Z0-9_]+")
RePathParam = re.compile("[.]{0,2}[/][^@]*[@][a-zA-Z0-9_]+")
ReEqual = re.compile("^\s*[=]\s*")


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
        self.__expression = None
        self.__pre_evaluated_value = None

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

    def hasExpression(self):
        return self.__expression is not None

    def validExpression(self):
        if not self.hasExpression():
            return True

        value = self.__evalExpression(self.__expression)

        if value is None:
            return False

        elif isinstance(value, self.__type_class):
            return True

        elif isinstance(value, Number) and issubclass(self.__type_class, Number):
            return True

        elif isinstance(value, basestring) and issubclass(self.__type_class, basestring):
            return True

        return False

    def activate(self):
        if not self.hasExpression():
            self.__pre_evaluated_value = None
            return

        value = self.__evalExpression(self.__expression)

        if value is None:
            self.__pre_evaluated_value = self.__type_class()
        elif isinstance(value, self.__type_class):
            self.__pre_evaluated_value =  value
        elif isinstance(value, Number) and issubclass(self.__type_class, Number):
            self.__pre_evaluated_value = self.__type_class(value)
        elif isinstance(value, basestring) and issubclass(self.__type_class, basestring):
            self.__pre_evaluated_value = str(value)
        else:
            self.__pre_evaluated_value = self.__type_class()

    def terminate(self):
        self.__pre_evaluated_value = None

    def typeClass(self):
        return self.__type_class

    def __popEqual(self, expression):
        return ReEqual.sub("", expression)

    def __resolveTokens(self, expression):
        subs = []
        tokens = set()

        for tkn_txt in ReContextParam.findall(expression):
            tokens.add(tkn_txt[1:])

        if not tokens:
            return expression

        ctx = self.__getContext()

        for tkn in tokens:
            val = None
            val = ctx.get(tkn, None)
            if val is None:
                val = os.environ.get(tkn, None)

            if val is None:
                continue

            subs.append((re.compile("[$]{}".format(tkn)), str(val)))

        for reg, v in subs:
            expression = reg.sub(str(v), expression)

        return expression

    def __resolvePaths(self, expression):
        pths = set()
        subs = []

        for pth in RePathParam.findall(expression):
            pths.add(pth)

        if not pths:
            return expression

        top = self.ancestor()
        if top is None:
            return expression

        for pth in pths:
            if pth.count("@") != 1:
                continue

            t_path, t_param = pth.split("@")

            bloc_full = os.path.abspath(os.path.join(self.path().split("@")[0], t_path)).replace("\\", "/")

            bloc = top.findBlock(bloc_full)

            if bloc is None:
                continue

            p = bloc.param(t_param)
            if p is None:
                continue

            if p == self:
                continue

            subs.append((pth, re.compile(pth.replace(".", "[.]").replace("\/", "[/]")), str(p.get())))

        subs.sort(cmp=lambda x, y: cmp(len(x[0]), len(y[0])), reverse=True)

        for _, reg, v in subs:
            expression = reg.sub(v, expression)

        return expression

    def __resolveExpression(self, expression):
        return self.__popEqual(self.__resolveTokens(self.__resolvePaths(expression)))

    def __evalExpression(self, expression):
        exp = self.__resolveExpression(expression)
        try:
            return eval(exp)
        except Exception as e:
            return None

    def __getContext(self):
        cur = None
        top = self.ancestor()

        return top.getContext()

    def setExpression(self, expression):
        if expression is None:
            self.__expression = None
            return True

        if ReEqual.search(expression) is None:
            return False

        self.__expression = expression

        return True

    def getExpression(self):
        return self.__expression

    def get(self):
        if not self.hasExpression():
            return self.__value

        if self.__pre_evaluated_value is not None:
            return self.__pre_evaluated_value

        value = self.__evalExpression(self.__expression)

        if value is None:
            return self.__type_class()

        if isinstance(value, self.__type_class):
            return value

        if isinstance(value, Number) and issubclass(self.__type_class, Number):
            return self.__type_class(value)

        if isinstance(value, basestring) and issubclass(self.__type_class, basestring):
            return str(value)

        return self.__type_class()

    def set(self, value):
        if isinstance(value, self.__type_class):
            self.__value = value
            return True

        if isinstance(value, Number) and issubclass(self.__type_class, Number):
            self.__value = self.__type_class(value)
            return True

        if isinstance(value, basestring) and issubclass(self.__type_class, basestring):
            self.__value = str(value)
            return True

        return False


class EnumParameter(core.ParameterBase):
    def __new__(self, name, vList, value=None, parent=None):
        if value is not None and not isinstance(value, int):
            return None

        if not isinstance(vList, list):
            return None

        if len(vList) < 1:
            return None

        return super(EnumParameter, self).__new__(self, name, typeClass=int, value=value, parent=parent)

    def __init__(self, name, vList, value=None, parent=None):
        super(EnumParameter, self).__init__(name, typeClass=int, value=value, parent=parent)
        self.__value = value
        if value is None or value < 0 or value > len(vList):
            self.__value = 0

        self.__enum = {}
        for i, v in enumerate(vList):
            self.__enum[i] = v

    def typeClass(self):
        return core.PBEnum

    def getLabels(self):
        return self.__enum.values()

    def getLabel(self):
        return self.__enum[self.__value]

    def get(self):
        return self.__value

    def set(self, value):
        if not isinstance(value, Number):
            return False

        if value < 0 or value > len(self.__enum):
            return False

        self.__value = int(value)

        return True
