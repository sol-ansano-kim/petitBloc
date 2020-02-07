from petitBloc import block
from petitBloc import anytype


class Compare(block.Block):
    def __init__(self):
        super(Compare, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(bool, "result")
        self.addEnumParam("operator", [">", ">=", "==", "<=", "<"], value=2)

    def run(self):
        self.__i1_eop = False
        self.__i2_eop = False
        self.__v1 = None
        self.__v2 = None
        super(Compare, self).run()

    def process(self):
        if not self.__i1_eop:
            in1 = self.input("input1").receive()
            if in1.isEOP():
                self.__i1_eop = True
            else:
                self.__v1 = in1.value()

        if self.__v1 is None:
            return False

        if not self.__i2_eop:
            in2 = self.input("input2").receive()
            if in2.isEOP():
                self.__i2_eop = True
            else:
                self.__v2 = in2.value()

        if self.__v2 is None:
            return False

        if self.__i1_eop and self.__i2_eop:
            return False

        oper = self.param("operator").get()

        if oper is 0:
            self.output("result").send(self.__v1 > self.__v2)

        elif oper is 1:
            self.output("result").send(self.__v1 >= self.__v2)

        elif oper is 2:
            self.output("result").send(self.__v1 == self.__v2)

        elif oper is 3:
            self.output("result").send(self.__v1 <= self.__v2)

        else:
            self.output("result").send(self.__v1 < self.__v2)

        return True


class Choice(block.Block):
    def __init__(self):
        super(Choice, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "trueValue")
        self.addInput(anytype.AnyType, "falseValue")
        self.addInput(bool, "condition")
        self.addOutput(anytype.AnyType, "output")

    def run(self):
        self.__i1_eop = False
        self.__i2_eop = False
        self.__v1 = None
        self.__v2 = None
        super(Choice, self).run()

    def process(self):
        if not self.__i1_eop:
            in1 = self.input("trueValue").receive()
            if in1.isEOP():
                self.__i1_eop = True
            else:
                self.__v1 = in1.value()

        if self.__v1 is None:
            return False

        if not self.__i2_eop:
            in2 = self.input("falseValue").receive()
            if in2.isEOP():
                self.__i2_eop = True
            else:
                self.__v2 = in2.value()

        if self.__v2 is None:
            return False

        if self.__i1_eop and self.__i2_eop:
            return False

        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        self.output("output").send(self.__v1 if con else self.__v2)

        return True


class Selector(block.Block):
    def __init__(self):
        super(Selector, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "value")
        self.addInput(bool, "condition")
        self.addOutput(anytype.AnyType, "matched")
        self.addOutput(anytype.AnyType, "unmatched")

    def process(self):
        val_p = self.input("value").receive()
        if val_p.isEOP():
            return False

        val = val_p.value()
        val_p.drop()

        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        if con:
            self.output("matched").send(val)

        else:
            self.output("unmatched").send(val)

        return True


class Repeat(block.Block):
    def __init__(self):
        super(Repeat, self).__init__()

    def initialize(self):
        self.addInput(int, "time")
        self.addInput(anytype.AnyType, "inValue")
        self.addOutput(anytype.AnyType, "outValue")

    def process(self):
        time_p = self.input("time").receive()
        if time_p.isEOP():
            return False

        time = time_p.value()
        time_p.drop()

        value_p = self.input("inValue").receive()
        if value_p.isEOP():
            return False

        value = value_p.value()
        value_p.drop()

        op = self.output("outValue")
        for i in range(time):
            op.send(value)

        return True
