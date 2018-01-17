from petitBloc import block
import sys


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
        self.addParam(float, "value", 0.0)

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
        self.addParam(float, "value", 0.0)

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
