from petitBloc import block


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
        self.addInput(float, "true")
        self.addInput(float, "false")
        self.addInput(bool, "condition")
        self.addOutput(float, "output")

    def run(self):
        self.__i1_eop = False
        self.__i2_eop = False
        self.__v1 = None
        self.__v2 = None
        super(Choice, self).run()

    def process(self):
        if not self.__i1_eop:
            in1 = self.input("true").receive()
            if in1.isEOP():
                self.__i1_eop = True
            else:
                self.__v1 = in1.value()

        if self.__v1 is None:
            return False

        if not self.__i2_eop:
            in2 = self.input("false").receive()
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


class BoolSelector(block.Block):
    def __init__(self):
        super(BoolSelector, self).__init__()

    def initialize(self):
        self.addInput(bool, "value")
        self.addInput(bool, "condition")
        self.addOutput(bool, "matched")
        self.addOutput(bool, "unmatched")

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


class IntSelector(block.Block):
    def __init__(self):
        super(IntSelector, self).__init__()

    def initialize(self):
        self.addInput(int, "value")
        self.addInput(bool, "condition")
        self.addOutput(int, "matched")
        self.addOutput(int, "unmatched")

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


class FloatSelector(block.Block):
    def __init__(self):
        super(FloatSelector, self).__init__()

    def initialize(self):
        self.addInput(float, "value")
        self.addInput(bool, "condition")
        self.addOutput(float, "matched")
        self.addOutput(float, "unmatched")

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


class StringSelector(block.Block):
    def __init__(self):
        super(StringSelector, self).__init__()

    def initialize(self):
        self.addInput(str, "value")
        self.addInput(bool, "condition")
        self.addOutput(str, "matched")
        self.addOutput(str, "unmatched")

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
