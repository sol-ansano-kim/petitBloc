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


class IntArrayGet(block.Block):
    def __init__(self):
        super(IntArrayGet, self).__init__()

    def initialize(self):
        self.addInput(list, "array")
        self.addInput(int, "index")
        self.addOutput(int, "value")

    def run(self):
        self.__index_eop = False
        self.__index_dump = None
        super(IntArrayGet, self).run()

    def process(self):
        if not self.__index_eop:
            index_p = self.input("index").receive()
            if index_p.isEOP():
                self.__index_eop = True
            else:
                self.__index_dump = index_p.value()
                index_p.drop()

        if self.__index_dump is None:
            return False

        arr_p = self.input("array").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        self.output("value").send(arr[self.__index_dump])
        return True


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


class FloatArrayGet(block.Block):
    def __init__(self):
        super(FloatArrayGet, self).__init__()

    def initialize(self):
        self.addInput(list, "array")
        self.addInput(int, "index")
        self.addOutput(float, "value")

    def run(self):
        self.__index_eop = False
        self.__index_dump = None
        super(FloatArrayGet, self).run()

    def process(self):
        if not self.__index_eop:
            index_p = self.input("index").receive()
            if index_p.isEOP():
                self.__index_eop = True
            else:
                self.__index_dump = index_p.value()
                index_p.drop()

        if self.__index_dump is None:
            return False

        arr_p = self.input("array").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        self.output("value").send(arr[self.__index_dump])
        return True


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


class BoolArrayGet(block.Block):
    def __init__(self):
        super(BoolArrayGet, self).__init__()

    def initialize(self):
        self.addInput(list, "array")
        self.addInput(int, "index")
        self.addOutput(bool, "value")

    def run(self):
        self.__index_eop = False
        self.__index_dump = None
        super(BoolArrayGet, self).run()

    def process(self):
        if not self.__index_eop:
            index_p = self.input("index").receive()
            if index_p.isEOP():
                self.__index_eop = True
            else:
                self.__index_dump = index_p.value()
                index_p.drop()

        if self.__index_dump is None:
            return False

        arr_p = self.input("array").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        self.output("value").send(arr[self.__index_dump])
        return True


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


class StringArrayGet(block.Block):
    def __init__(self):
        super(StringArrayGet, self).__init__()

    def initialize(self):
        self.addInput(list, "array")
        self.addInput(int, "index")
        self.addOutput(str, "value")

    def run(self):
        self.__index_eop = False
        self.__index_dump = None
        super(StringArrayGet, self).run()

    def process(self):
        if not self.__index_eop:
            index_p = self.input("index").receive()
            if index_p.isEOP():
                self.__index_eop = True
            else:
                self.__index_dump = index_p.value()
                index_p.drop()

        if self.__index_dump is None:
            return False

        arr_p = self.input("array").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        self.output("value").send(arr[self.__index_dump])
        return True


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


class ArrayLen(block.Block):
    def __init__(self):
        super(ArrayLen, self).__init__()

    def initialize(self):
        self.addInput(list, "array")
        self.addOutput(int, "len")

    def process(self):
        arr = self.input("array").receive()
        if arr.isEOP():
            return False

        self.output("len").send(len(arr.value()))

        return True
