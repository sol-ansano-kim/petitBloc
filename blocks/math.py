from petitBloc import block


class Plus(block.Block):
    def __init__(self):
        super(Plus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def process(self):
        v1 = None
        v2 = None

        in1 = self.input("input1").receive()
        in2 = self.input("input2").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if v1 is None or v2 is None:
            return False

        self.output("result").send(v1 + v2)

        return True


class Minus(block.Block):
    def __init__(self):
        super(Minus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def process(self):
        v1 = None
        v2 = None

        in1 = self.input("input1").receive()
        in2 = self.input("input2").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if v1 is None or v2 is None:
            return False

        self.output("result").send(v1 - v2)

        return True


class Multiply(block.Block):
    def __init__(self):
        super(Multiply, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def process(self):
        v1 = None
        v2 = None

        in1 = self.input("input1").receive()
        in2 = self.input("input2").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if v1 is None or v2 is None:
            return False

        self.output("result").send(v1 * v2)

        return True


class Divide(block.Block):
    def __init__(self):
        super(Divide, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def process(self):
        v1 = None
        v2 = None

        in1 = self.input("input1").receive()
        in2 = self.input("input2").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if v1 is None or v2 is None:
            return False

        if v2 == 0:
            self.output("result").send(0)
            return True

        self.output("result").send(v1 / v2)

        return True
