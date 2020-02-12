from petitBloc import block
from petitBloc import anytype


class Compare(block.Block):
    def __init__(self):
        super(Compare, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(bool, "output")
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
            self.output("output").send(v1 > v2)

        elif oper is 1:
            self.output("output").send(v1 >= v2)

        elif oper is 2:
            self.output("output").send(v1 == v2)

        elif oper is 3:
            self.output("output").send(v1 <= v2)

        else:
            self.output("output").send(v1 < v2)

        return True


class BooleanOp(block.Block):
    def __init__(self):
        super(BooleanOp, self).__init__()

    def initialize(self):
        self.addInput(bool, "input1")
        self.addInput(bool, "input2")
        self.addOutput(bool, "output")
        self.addEnumParam("operator", ["and", "or", "xor", "not"], value=0)

    def process(self):
        oper = self.param("operator").get()
        single = (oper == 3)
        
        v1_p = self.input("input1").receive()
        if v1_p.isEOP():
            if not single:
                return False
            v1 = None
        else:
            v1 = v1_p.value()
            v1_p.drop()

        v2_p = self.input("input2").receive()
        if v2_p.isEOP():
            if not single:
                return False
            v2 = None
        else:
            v2 = v2_p.value()
            v2_p.drop()

        if oper == 0:
            self.output("output").send(v1 and v2)

        elif oper == 1:
            self.output("output").send(v1 or v2)

        elif oper == 2:
            self.output("output").send((v1 and not v2) or (v2 and not v1))

        else:
            if v1 is None:
                if v2 is None:
                    # no input set, undefined
                    return False
                self.output("output").send(not v2)
            else:
                if v2 is not None:
                    # both input set, which one should that be?
                    return False
                self.output("output").send(not v1)

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
        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        if con:
            fv_p = self.input("falseValue").receive()
            if not fv_p.isEOP():
                fv_p.drop()

            tv_p = self.input("trueValue").receive()
            if tv_p.isEOP():
                return

            tv = tv_p.value()
            tv_p.drop()

            self.output("output").send(tv)

        else:
            tv_p = self.input("trueValue").receive()
            if not tv_p.isEOP():
                tv_p.drop()

            fv_p = self.input("falseValue").receive()
            if fv_p.isEOP():
                return

            fv = fv_p.value()
            fv_p.drop()

            self.output("output").send(fv)

        return True


class ReRoute(block.Block):
    def __init__(self):
        super(ReRoute, self).__init__()

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
