from petitBloc import block
from petitBloc import anytype


class Plus(block.Block):
    def __init__(self):
        super(Plus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "output")

    def process(self):
        in1_p = self.input("input1").receive()
        if in1_p.isEOP():
            return False

        in1 = in1_p.value()
        in1_p.drop()

        in2_p = self.input("input2").receive()
        if in2_p.isEOP():
            return False

        in2 = in2_p.value()
        in2_p.drop()

        self.output("output").send(in1 + in2)

        return True


class Minus(block.Block):
    def __init__(self):
        super(Minus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "output")

    def process(self):
        in1_p = self.input("input1").receive()
        if in1_p.isEOP():
            return False

        in1 = in1_p.value()
        in1_p.drop()

        in2_p = self.input("input2").receive()
        if in2_p.isEOP():
            return False

        in2 = in2_p.value()
        in2_p.drop()

        self.output("output").send(in1 - in2)

        return True


class Multiply(block.Block):
    def __init__(self):
        super(Multiply, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "output")

    def process(self):
        in1_p = self.input("input1").receive()
        if in1_p.isEOP():
            return False

        in1 = in1_p.value()
        in1_p.drop()

        in2_p = self.input("input2").receive()
        if in2_p.isEOP():
            return False

        in2 = in2_p.value()
        in2_p.drop()

        self.output("output").send(in1 * in2)

        return True


class Divide(block.Block):
    def __init__(self):
        super(Divide, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "output")

    def process(self):
        in1_p = self.input("input1").receive()
        if in1_p.isEOP():
            return False

        in1 = in1_p.value()
        in1_p.drop()

        in2_p = self.input("input2").receive()
        if in2_p.isEOP():
            return False

        in2 = in2_p.value()
        in2_p.drop()

        if in2 == 0:
            self.output("output").send(0)
            self.warn("'{}' division by zero division. result will be 0".format(in1))
            return True

        self.output("output").send(in1 / in2)

        return True


class ToInt(block.Block):
    def __init__(self):
        super(ToInt, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "input")
        self.addOutput(int, "output")

    def process(self):
        in_p = self.input("input").receive()
        if in_p.isEOP():
            return False

        self.output("output").send(int(in_p.value()))
        in_p.drop()

        return True


class ToFloat(block.Block):
    def __init__(self):
        super(ToFloat, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "input")
        self.addOutput(float, "output")

    def process(self):
        in_p = self.input("input").receive()
        if in_p.isEOP():
            return False

        self.output("output").send(float(in_p.value()))
        in_p.drop()

        return True


class ToBool(block.Block):
    def __init__(self):
        super(ToBool, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "input")
        self.addOutput(bool, "output")

    def process(self):
        in_p = self.input("input").receive()
        if in_p.isEOP():
            return False

        self.output("output").send(bool(in_p.value()))
        in_p.drop()

        return True


class Min(block.Block):
    def __init__(self):
        super(Min, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "input1")
        self.addInput(anytype.AnyType, "input2")
        self.addOutput(anytype.AnyType, "output")

    def process(self):
        in1_p = self.input("input1").receive()
        if in1_p.isEOP():
            return False

        in1 = in1_p.value()
        in1_p.drop()

        in2_p = self.input("input2").receive()
        if in2_p.isEOP():
            return False

        in2 = in2_p.value()
        in2_p.drop()

        self.output("output").send(min(in1, in2))

        return True


class Max(block.Block):
    def __init__(self):
        super(Max, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "input1")
        self.addInput(anytype.AnyType, "input2")
        self.addOutput(anytype.AnyType, "output")

    def process(self):
        in1_p = self.input("input1").receive()
        if in1_p.isEOP():
            return False

        in1 = in1_p.value()
        in1_p.drop()

        in2_p = self.input("input2").receive()
        if in2_p.isEOP():
            return False

        in2 = in2_p.value()
        in2_p.drop()

        self.output("output").send(max(in1, in2))

        return True

