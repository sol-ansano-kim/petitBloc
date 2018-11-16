from petitBloc import block
from petitBloc import anytype


class List(block.Block):
    def __init__(self):
        super(List, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "value")
        self.addOutput(list, "list")

    def run(self):
        array = []

        inp = self.input("value")
        while (True):
            p = inp.receive()
            if p.isEOP():
                break

            array.append(p.value())

        self.output("list").send(array)


class ListGet(block.Block):
    def __init__(self):
        super(ListGet, self).__init__()

    def initialize(self):
        self.addInput(list, "list")
        self.addInput(int, "index")
        self.addOutput(anytype.AnyType, "value")

    def run(self):
        self.__index_eop = False
        self.__index_dump = None
        super(ListGet, self).run()

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

        arr_p = self.input("list").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        self.output("value").send(arr[self.__index_dump])
        return True


class ListIter(block.Block):
    def __init__(self):
        super(ListIter, self).__init__()

    def initialize(self):
        self.addOutput(anytype.AnyType, "value")
        self.addInput(list, "list")

    def process(self):
        arr = self.input("list").receive()
        if arr.isEOP():
            return False

        for i in arr.value():
            self.output("value").send(i)

        return True


class ListLength(block.Block):
    def __init__(self):
        super(ListLength, self).__init__()

    def initialize(self):
        self.addInput(list, "list")
        self.addOutput(int, "len")

    def process(self):
        arr = self.input("list").receive()
        if arr.isEOP():
            return False

        self.output("len").send(len(arr.value()))

        return True


class ListAppend(block.Block):
    def __init__(self):
        super(ListAppend, self).__init__()

    def initialize(self):
        self.addInput(list, "list")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(list, "outList")

    def process(self):
        arr_p = self.input("list").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        value_p = self.input("value").receive()
        if value_p.isEOP():
            return False

        value = value_p.value()
        value_p.drop()

        arr.append(value)

        self.output("outList").send(arr)

        return True


class ListExtend(block.Block):
    def __init__(self):
        super(ListExtend, self).__init__()

    def initialize(self):
        self.addInput(list, "listA")
        self.addInput(list, "listB")
        self.addOutput(list, "extended")

    def process(self):
        arra_p = self.input("listA").receive()
        if arra_p.isEOP():
            return False

        arra = arra_p.value()
        arra_p.drop()

        arrb_p = self.input("listB").receive()
        if arrb_p.isEOP():
            return False

        arrb = arrb_p.value()
        arrb_p.drop()

        arra.extend(arrb)

        self.output("extended").send(arra)

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
