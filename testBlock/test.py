from petitBloc import block
import multiprocessing


class MakeNumbers(block.Block):
    def __init__(self, name="", parent=None):
        super(MakeNumbers, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addOutput(float)

    def process(self):
        for n in range(100):
            self.output(0).send(n)

        return False


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


class Mult(block.Block):
    def __init__(self, name="", parent=None):
        super(Mult, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.output(0).send(in_f.value() * 1.1)
        in_f.drop()

        return True


class Dump(block.Block):
    def __init__(self, name="", parent=None):
        super(Dump, self).__init__(name=name, parent=parent)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(float)

    def flush(self):
        while (not self.dmp.empty()):
            print self.dmp.get()

        self.dmp.close()
        del self.dmp
        self.dmp = multiprocessing.Queue()

    def run(self):
        while (True):
            if not self.process():
                break

        self.flush()

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        self.dmp.put(in_f.value())
        in_f.drop()

        return True
