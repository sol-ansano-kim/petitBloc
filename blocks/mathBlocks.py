from petitBloc import block


class Plus(block.Block):
    def __init__(self):
        super(Plus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

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

        self.output("result").send(in1 + in2)

        return True


class Minus(block.Block):
    def __init__(self):
        super(Minus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

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

        self.output("result").send(in1 - in2)

        return True


class Multiply(block.Block):
    def __init__(self):
        super(Multiply, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

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

        self.output("result").send(in1 * in2)

        return True


class Divide(block.Block):
    def __init__(self):
        super(Divide, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

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
            self.output("result").send(0)
            self.warn("'{}' division by zero division. result will be 0".format(in1))
            return True

        self.output("result").send(in1 / in2)

        return True


class CastToInt(block.Block):
    def __init__(self):
        super(CastToInt, self).__init__()

    def initialize(self):
        self.addInput(float, "input")
        self.addOutput(int, "output")

    def process(self):
        in_p = self.input("input").receive()
        if in_p.isEOP():
            return False

        self.output("output").send(in_p.value())
        in_p.drop()

        return True


class CastToFloat(block.Block):
    def __init__(self):
        super(CastToFloat, self).__init__()

    def initialize(self):
        self.addInput(float, "input")
        self.addOutput(float, "output")

    def process(self):
        in_p = self.input("input").receive()
        if in_p.isEOP():
            return False

        self.output("output").send(in_p.value())
        in_p.drop()

        return True


class CastToBool(block.Block):
    def __init__(self):
        super(CastToBool, self).__init__()

    def initialize(self):
        self.addInput(float, "input")
        self.addOutput(bool, "output")

    def process(self):
        in_p = self.input("input").receive()
        if in_p.isEOP():
            return False

        self.output("output").send(in_p.value())
        in_p.drop()

        return True
