from petitBloc import block
from petitBloc import anytype


class List(block.Block):
    def __init__(self):
        super(List, self).__init__()

    def initialize(self):
        self.addOutput(list, "list")

    def run(self):
        self.output("list").send([])


class ToList(block.Block):
    def __init__(self):
        super(ToList, self).__init__()

    def initialize(self):
        # TODO : size can be ignored. notice it visually
        self.addInput(int, "groupBy")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(list, "list")

    def run(self):
        gp = self.input("groupBy")
        vp = self.input("value")

        value_is_eop = False
        while (not value_is_eop):
            group_p = gp.receive()
            if group_p.isEOP():
                break

            group_size = group_p.value()
            group_p.drop()

            count = 0
            output = []
            while (count < group_size):
                value_p = vp.receive()
                if value_p.isEOP():
                    value_is_eop = True
                    break

                count += 1
                output.append(value_p.value())
                value_p.drop()

            self.output("list").send(output)

        if not value_is_eop:
            output = []

            while (True):
                value_p = vp.receive()
                if value_p.isEOP():
                    break

                output.append(value_p.value())
                value_p.drop()

            if len(output):
                self.output("list").send(output)


class ListHas(block.Block):
    def __init__(self):
        super(ListHas, self).__init__()

    def initialize(self):
        self.addInput(list, "list")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(bool, "has")

    def process(self):
        list_p = self.input("list").receive()
        if list_p.isEOP():
            return False

        lst = list_p.value()
        list_p.drop()

        value_p = self.input("value").receive()
        if value_p.isEOP():
            return False

        value = value_p.value()
        value_p.drop()

        self.output("has").send(value in lst)

        return True


class ListGet(block.Block):
    def __init__(self):
        super(ListGet, self).__init__()

    def initialize(self):
        self.addInput(list, "list")
        self.addInput(int, "index")
        self.addOutput(anytype.AnyType, "value")

    def process(self):
        arr_p = self.input("list").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        index_p = self.input("index").receive()
        if index_p.isEOP():
            return False

        index = index_p.value()
        index_p.drop()

        self.output("value").send(arr[index])

        return True


class ListSet(block.Block):
    def __init__(self):
        super(ListSet, self).__init__()

    def initialize(self):
        self.addInput(list, "inList")
        self.addInput(int, "index")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(list, "outList")

    def process(self):
        in_list_p = self.input("inList").receive()
        if in_list_p.isEOP():
            return False

        in_list = in_list_p.value()
        in_list_p.drop()

        index_p = self.input("index").receive()
        if index_p.isEOP():
            return False

        index = index_p.value()
        index_p.drop()

        value_p = self.input("value").receive()
        if value_p.isEOP():
            return False

        value = value_p.value()
        value_p.drop()

        in_list[index] = value

        self.output("outList").send(in_list)

        return True


class ListIter(block.Block):
    def __init__(self):
        super(ListIter, self).__init__()

    def initialize(self):
        self.addOutput(int, "index")
        self.addOutput(int, "length")
        self.addOutput(anytype.AnyType, "value")
        self.addInput(list, "list")

    def process(self):
        arr = self.input("list").receive()
        if arr.isEOP():
            return False

        values = arr.value()
        arr.drop()

        self.output("length").send(len(values))
        for i, v in enumerate(values):
            self.output("index").send(i)
            self.output("value").send(v)

        return True


class ListLength(block.Block):
    def __init__(self):
        super(ListLength, self).__init__()

    def initialize(self):
        self.addInput(list, "list")
        self.addOutput(int, "length")

    def process(self):
        arr = self.input("list").receive()
        if arr.isEOP():
            return False

        self.output("length").send(len(arr.value()))

        return True


class ListAppend(block.Block):
    def __init__(self):
        super(ListAppend, self).__init__()

    def initialize(self):
        self.addInput(list, "inList")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(list, "outList")

    def process(self):
        arr_p = self.input("inList").receive()
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


class ListRemove(block.Block):
    def __init__(self):
        super(ListRemove, self).__init__()

    def initialize(self):
        self.addInput(list, "inList")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(list, "outList")

    def process(self):
        arr_p = self.input("inList").receive()
        if arr_p.isEOP():
            return False

        arr = arr_p.value()
        arr_p.drop()

        value_p = self.input("value").receive()
        if value_p.isEOP():
            return False

        value = value_p.value()
        value_p.drop()

        if value in arr:
            arr.remove(value)

        self.output("outList").send(arr)

        return True


class ListExtend(block.Block):
    def __init__(self):
        super(ListExtend, self).__init__()

    def initialize(self):
        self.addInput(list, "listA")
        self.addInput(list, "listB")
        self.addOutput(list, "output")

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

        self.output("output").send(arra)

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
