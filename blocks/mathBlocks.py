from petitBloc import block


class Plus(block.Block):
    def __init__(self):
        super(Plus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def run(self):
        self.__i1_eop = False
        self.__i2_eop = False
        self.__v1 = None
        self.__v2 = None
        super(Plus, self).run()

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

        self.output("result").send(self.__v1 + self.__v2)

        return True


class Minus(block.Block):
    def __init__(self):
        super(Minus, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def run(self):
        self.__i1_eop = False
        self.__i2_eop = False
        self.__v1 = None
        self.__v2 = None
        super(Minus, self).run()

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

        self.output("result").send(self.__v1 - self.__v2)

        return True


class Multiply(block.Block):
    def __init__(self):
        super(Multiply, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def run(self):
        self.__i1_eop = False
        self.__i2_eop = False
        self.__v1 = None
        self.__v2 = None
        super(Multiply, self).run()

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

        self.output("result").send(self.__v1 * self.__v2)

        return True


class Divide(block.Block):
    def __init__(self):
        super(Divide, self).__init__()

    def initialize(self):
        self.addInput(float, "input1")
        self.addInput(float, "input2")
        self.addOutput(float, "result")

    def run(self):
        self.__i1_eop = False
        self.__i2_eop = False
        self.__v1 = None
        self.__v2 = None
        super(Divide, self).run()

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

        if self.__v2 == 0:
            self.output("result").send(0)
            return True

        self.output("result").send(self.__v1 / self.__v2)

        return True
