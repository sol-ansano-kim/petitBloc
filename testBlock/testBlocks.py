from petitBloc import block
import sys


class MakeNumbers(block.Block):
    def __init__(self, name="", parent=None):
        super(MakeNumbers, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addOutput(float)

    def run(self):
        for n in range(10):
            self.output(0).send(n)


class AddOne(block.Block):
    def __init__(self, name="", parent=None):
        super(AddOne, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(int)
        self.addOutput(int)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.output(0).send(in_f.value() + 1)
        in_f.drop()

        return True


class MultTwo(block.Block):
    def __init__(self, name="", parent=None):
        super(MultTwo, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.output(0).send(in_f.value() * 2)
        in_f.drop()

        return True


class Print(block.Block):
    def __init__(self, name="", parent=None):
        super(Print, self).__init__(name=name, parent=parent)
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
