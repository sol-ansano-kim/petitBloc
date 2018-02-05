from petitBloc import block


class IntArray(block.Block):
    def __init__(self):
        super(IntArray, self).__init__()

    def initialize(self):
        self.addInput(int, "value")
        self.addOutput(list, "array")

    def run(self):
        array = []

        inp = self.input("value")
        while (True):
            p = inp.receive()
            if p.isEOP():
                break

            array.append(p.value())

        self.output("array").send(array)


class IntArrayIter(block.Block):
    def __init__(self):
        super(IntArrayIter, self).__init__()

    def initialize(self):
        self.addOutput(int, "value")
        self.addInput(list, "array")

    def process(self):
        arr = self.input("array").receive()
        if arr.isEOP():
            return False

        for i in arr.value():
            self.output("value").send(int(i))

        return True


class FloatArray(block.Block):
    def __init__(self):
        super(FloatArray, self).__init__()

    def initialize(self):
        self.addInput(float, "value")
        self.addOutput(list, "array")

    def run(self):
        array = []

        inp = self.input("value")
        while (True):
            p = inp.receive()
            if p.isEOP():
                break

            array.append(p.value())

        self.output("array").send(array)


class FloatArrayIter(block.Block):
    def __init__(self):
        super(FloatArrayIter, self).__init__()

    def initialize(self):
        self.addOutput(float, "value")
        self.addInput(list, "array")

    def process(self):
        arr = self.input("array").receive()
        if arr.isEOP():
            return False

        for i in arr.value():
            self.output("value").send(float(i))

        return True


class BoolArray(block.Block):
    def __init__(self):
        super(BoolArray, self).__init__()

    def initialize(self):
        self.addInput(bool, "value")
        self.addOutput(list, "array")

    def run(self):
        array = []

        inp = self.input("value")
        while (True):
            p = inp.receive()
            if p.isEOP():
                break

            array.append(p.value())

        self.output("array").send(array)


class BoolArrayIter(block.Block):
    def __init__(self):
        super(BoolArrayIter, self).__init__()

    def initialize(self):
        self.addOutput(bool, "value")
        self.addInput(list, "array")

    def process(self):
        arr = self.input("array").receive()
        if arr.isEOP():
            return False

        for i in arr.value():
            self.output("value").send(bool(i))

        return True


class StringArray(block.Block):
    def __init__(self):
        super(StringArray, self).__init__()

    def initialize(self):
        self.addInput(str, "value")
        self.addOutput(list, "array")

    def run(self):
        array = []

        inp = self.input("value")
        while (True):
            p = inp.receive()
            if p.isEOP():
                break

            array.append(p.value())

        self.output("array").send(array)


class StringArrayIter(block.Block):
    def __init__(self):
        super(StringArrayIter, self).__init__()

    def initialize(self):
        self.addOutput(str, "value")
        self.addInput(list, "array")

    def process(self):
        arr = self.input("array").receive()
        if arr.isEOP():
            return False

        for i in arr.value():
            self.output("value").send(str(i))

        return True


class Range(block.Block):
    def __init__(self):
        super(Range, self).__init__()

    def initialize(self):
        self.addParam(int, "start")
        self.addParam(int, "stop")
        self.addParam(int, "step")
        self.addOutput(int, "value")

    def run(self):
        step = self.param("step").get()
        if step < 1:
            step = 1

        for n in range(self.param("start").get(), self.param("stop").get(), step):
            self.output(0).send(n)
