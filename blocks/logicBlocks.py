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

    def process(self):
        v1_p = self.input("input1").receive()
        if v1_p.isEOP():
            return False

        v1 = v1_p.value()
        v1_p.drop()

        v2_p = self.input("input2").receive()
        if v2_p.isEOP():
            return False

        v2 = v2_p.value()
        v2_p.drop()

        oper = self.param("operator").get()

        if oper is 0:
            self.output("result").send(v1 > v2)

        elif oper is 1:
            self.output("result").send(v1 >= v2)

        elif oper is 2:
            self.output("result").send(v1 == v2)

        elif oper is 3:
            self.output("result").send(v1 <= v2)

        else:
            self.output("result").send(v1 < v2)

        return True


class Choice(block.Block):
    def __init__(self):
        super(Choice, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "trueValue")
        self.addInput(anytype.AnyType, "falseValue")
        self.addInput(bool, "condition")
        self.addOutput(anytype.AnyType, "output")

    def process(self):
        tv_p = self.input("trueValue").receive()
        if tv_p.isEOP():
            return

        tv = tv_p.value()
        tv_p.drop()

        fv_p = self.input("falseValue").receive()
        if fv_p.isEOP():
            return

        fv = fv_p.value()
        fv_p.drop()

        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        self.output("output").send(tv if con else fv)

        return True


class Select(block.Block):
    def __init__(self):
        super(Select, self).__init__()

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


class Selector(Select):
    def __init__(self):
        super(Selector, self).__init__()

    def run(self):
        self.warn("'Selector' block is deprecated. Please use 'Select' block instead")
        super(Selector, self).run()


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


class DuplicateFlow(block.Block):
    def __init__(self):
        super(DuplicateFlow, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "flow")
        self.addInput(anytype.AnyType, "by")
        self.addOutput(anytype.AnyType, "output")

    def run(self):
        self.__flow_eop = False
        self.__flow_dumped = False
        self.__flow_value = None
        super(DuplicateFlow, self).run()

    def process(self):
        if not self.__flow_eop:
            flow_p = self.input("flow").receive()
            if flow_p.isEOP():
                self.__flow_eop = True
            else:
                self.__flow_dumped = True
                self.__flow_value = flow_p.value()

        if not self.__flow_dumped:
            return False

        by_p = self.input("by").receive()
        if by_p.isEOP():
            return False

        by_p.drop()

        self.output("output").send(self.__flow_value)

        return True
