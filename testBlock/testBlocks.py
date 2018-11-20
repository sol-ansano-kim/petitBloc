from petitBloc import block
from petitBloc import dastype
import sys
import os
os.environ["DAS_SCHEMA_PATH"] = os.path.dirname(__file__)


UseDas = True
try:
    import das
except:
    UseDas = False


class TestObject(object):
    def __init__(self):
        super(TestObject, self).__init__()


class StyleCheck(block.Block):
    def __init__(self, name="", parent=None):
        super(StyleCheck, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(bool, "boolIn")
        self.addInput(int, "intIn")
        self.addInput(float, "floatIn")
        self.addInput(str, "strIn")
        self.addInput(TestObject, "objectIn")
        self.addOutput(bool, "boolOut")
        self.addOutput(int, "intOut")
        self.addOutput(float, "floatOut")
        self.addOutput(str, "strOut")
        self.addOutput(TestObject, "objectOut")


class MakeNumbers(block.Block):
    def __init__(self, name="", parent=None):
        super(MakeNumbers, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addOutput(float)
        self.addParam(int, "start", 0)
        self.addParam(int, "stop", 10)
        self.addParam(int, "step", 1)

    def run(self):
        start = self.param("start").get()
        stop = self.param("stop").get()
        step = self.param("step").get()
        if step < 1:
            step = 1

        for n in range(start, stop, step):
            self.output(0).send(n)


class Plus(block.Block):
    def __init__(self, name="", parent=None):
        super(Plus, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)
        self.addParam(float, "value", 0.0)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.output(0).send(in_f.value() + self.param("value").get())
        in_f.drop()

        return True


class Minus(block.Block):
    def __init__(self, name="", parent=None):
        super(Minus, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)
        self.addParam(float, "value", 0.0)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.output(0).send(in_f.value() - self.param("value").get())
        in_f.drop()

        return True


class Multiply(block.Block):
    def __init__(self, name="", parent=None):
        super(Multiply, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)
        self.addParam(float, "value", 1.0)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.output(0).send(in_f.value() * self.param("value").get())
        in_f.drop()

        return True


class Divide(block.Block):
    def __init__(self, name="", parent=None):
        super(Divide, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)
        self.addParam(float, "value", 1.0)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.output(0).send(in_f.value() / self.param("value").get())
        in_f.drop()

        return True


class DumpPrint(block.Block):
    def __init__(self, name="", parent=None):
        super(DumpPrint, self).__init__(name=name, parent=parent)
        self.__values = []

    def initialize(self):
        self.addInput(float)

    def run(self):
        self.__values = []
        while (True):
            if not self.process():
                break

        print(self.__values)
        sys.stdout.flush()

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.__values.append(in_f.value())

        in_f.drop()

        return True


class RaiseError(block.Block):
    def __init__(self, name="", parent=None):
        super(RaiseError, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(int)
        self.addParam(int, "value")

    def process(self):
        self.warn("warn test")
        in_i = self.input(0).receive()
        if in_i.isEOP():
            return False

        if in_i.value() == self.param("value").get():
            raise Exception, "Raise ERROR for testing"

        self.debug("debug test : {}".format(in_i.value()))
        in_i.drop()

        return True


class MakeDasInt(block.Block):
    def __init__(self):
        super(MakeDasInt, self).__init__()

    def initialize(self):
        self.addParam(int, "int")
        self.addOutput(dastype.DasType("dasTest.intType"), "dasInt")

    def run(self):
        self.output("dasInt").send(self.param("int").get())


class MakeDasFloat(block.Block):
    def __init__(self):
        super(MakeDasFloat, self).__init__()

    def initialize(self):
        self.addParam(float, "flt")
        self.addOutput(dastype.DasType("dasTest.floatType"), "dasFlt")

    def run(self):
        self.output("dasFlt").send(self.param("flt").get())


class MakeDasString(block.Block):
    def __init__(self):
        super(MakeDasString, self).__init__()

    def initialize(self):
        self.addParam(str, "str")
        self.addOutput(dastype.DasType("dasTest.stringType"), "dasStr")

    def run(self):
        self.output("dasStr").send(self.param("str").get())


class MakeDasStruct(block.Block):
    def __init__(self):
        super(MakeDasStruct, self).__init__()

    def initialize(self):
        self.addParam(int, "int")
        self.addParam(float, "flt")
        self.addParam(str, "str")
        self.addOutput(dastype.DasType("dasTest.struct"), "dasStruct")

    def run(self):
        if UseDas:
            st = das.make_default("dasTest.struct")
            st["i"] = self.param("int").get()
            st["f"] = self.param("flt").get()
            st["s"] = self.param("str").get()
        else:
            st = {"i": self.param("int").get(), "f": self.param("flt").get(), "s": self.param("str").get()}
        self.output("dasStruct").send(st)


class DasBlock(block.Block):
    def __init__(self):
        super(DasBlock, self).__init__()

    def initialize(self):
        self.addInput(dastype.DasType("dasTest.intType"), "inInt")
        self.addInput(dastype.DasType("dasTest.floatType"), "inFloat")
        self.addInput(dastype.DasType("dasTest.stringType"), "inString")
        self.addInput(dastype.DasType("dasTest.struct"), "inStruct")

    def run(self):
        self.__int_eop = False
        self.__flt_eop = False
        self.__str_eop = False
        self.__struct_eop = False
        super(DasBlock, self).run()

    def process(self):
        ip = self.input("inInt")
        fp = self.input("inFloat")
        sp = self.input("inString")
        stp = self.input("inStruct")

        if not self.__int_eop:
            ipp = ip.receive()
            if ipp.isEOP():
                self.__int_eop = True
            else:
                v = ipp.value()
                ipp.drop()

        if not self.__flt_eop:
            fpp = fp.receive()
            if fpp.isEOP():
                self.__flt_eop = True
            else:
                v = fpp.value()
                fpp.drop()

        if not self.__str_eop:
            spp = sp.receive()
            if spp.isEOP():
                self.__str_eop = True
            else:
                v = spp.value()
                spp.drop()

        if not self.__struct_eop:
            stpp = stp.receive()
            if stpp.isEOP():
                self.__struct_eop = True
            else:
                v = stpp.value()
                stpp.drop()

        if self.__int_eop and self.__flt_eop and self.__str_eop and self.__struct_eop:
            return False

        return True
