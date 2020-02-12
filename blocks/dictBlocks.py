from petitBloc import block
from petitBloc import anytype


class Dict(block.Block):
    def __init__(self):
        super(Dict, self).__init__()

    def initialize(self):
        self.addOutput(dict, "dict")

    def run(self):
        self.output("dict").send({})


class ToDict(block.Block):
    def __init__(self):
        super(ToDict, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "key")
        self.addInput(anytype.AnyType, "value")
        self.addInput(int, "groupBy")
        self.addOutput(dict, "dict")

    def run(self):
        output = {}
        gp = self.input("groupBy")
        kp = self.input("key")
        vp = self.input("value")

        is_eop = False
        while (not is_eop):
            group_p = gp.receive()
            if group_p.isEOP():
                break

            group_size = group_p.value()
            group_p.drop()

            count = 0
            output = {}
            while (count < group_size):
                key_p = kp.receive()
                value_p = vp.receive()
                if key_p.isEOP():
                    if not value_p.isEOP():
                        value_p.drop()
                    is_eop = True
                    break
                if value_p.isEOP():
                    if not key_p.isEOP():
                        key_p.drop()
                    is_eop = True
                    break

                count += 1
                output[key_p.value()] = value_p.value()
                key_p.drop()
                value_p.drop()

            self.output("dict").send(output)

        if not is_eop:
            output = {}

            while (True):
                key_p = kp.receive()
                if key_p.isEOP():
                    break

                value_p = vp.receive()
                if value_p.isEOP():
                    break

                output[key_p.value()] = value_p.value()
                key_p.drop()
                value_p.drop()

            if len(output):
                self.output("dict").send(output)


class DictHas(block.Block):
    def __init__(self):
        super(DictHas, self).__init__()

    def initialize(self):
        self.addInput(dict, "dict")
        self.addInput(anytype.AnyType, "key")
        self.addOutput(bool, "has")

    def process(self):
        dict_p = self.input("dict").receive()
        if dict_p.isEOP():
            return False

        dt = dict_p.value()
        dict_p.drop()

        key_p = self.input("key").receive()
        if key_p.isEOP():
            return False

        key = key_p.value()
        key_p.drop()

        self.output("has").send(key in dt)

        return True


class DictGet(block.Block):
    def __init__(self):
        super(DictGet, self).__init__()

    def initialize(self):
        self.addInput(dict, "dict")
        self.addInput(anytype.AnyType, "key")
        self.addOutput(anytype.AnyType, "value")

    def process(self):
        dict_p = self.input("dict").receive()
        if dict_p.isEOP():
            return False

        dt = dict_p.value()
        dict_p.drop()

        key_p = self.input("key").receive()
        if key_p.isEOP():
            return False

        key = key_p.value()
        key_p.drop()

        self.output("value").send(dt[key])

        return True


class DictSet(block.Block):
    def __init__(self):
        super(DictSet, self).__init__()

    def initialize(self):
        self.addInput(dict, "inDict")
        self.addInput(anytype.AnyType, "key")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(dict, "outDict")

    def process(self):
        dict_p = self.input("inDict").receive()
        if dict_p.isEOP():
            return False

        dt = dict_p.value()
        dict_p.drop()

        key_p = self.input("key").receive()
        if key_p.isEOP():
            return False

        key = key_p.value()
        key_p.drop()

        value_p = self.input("value").receive()
        if value_p.isEOP():
            return False

        value = value_p.value()
        value_p.drop()

        dt[key] = value

        self.output("outDict").send(dt)

        return True


class DictKeys(block.Block):
    def __init__(self):
        super(DictKeys, self).__init__()

    def initialize(self):
        self.addInput(dict, "dict")
        self.addOutput(list, "keys")

    def process(self):
        dict_p = self.input("dict").receive()
        if dict_p.isEOP():
            return False

        keys = dict_p.value().keys()
        dict_p.drop()

        self.output("keys").send(keys)

        return True


class DictValues(block.Block):
    def __init__(self):
        super(DictValues, self).__init__()

    def initialize(self):
        self.addInput(dict, "dict")
        self.addOutput(list, "values")

    def process(self):
        dict_p = self.input("dict").receive()
        if dict_p.isEOP():
            return False

        values = dict_p.value().values()
        dict_p.drop()

        self.output("values").send(values)

        return True


class DictItems(block.Block):
    def __init__(self):
        super(DictItems, self).__init__()

    def initialize(self):
        self.addInput(dict, "dict")
        self.addOutput(list, "keys")
        self.addOutput(list, "values")

    def process(self):
        dict_p = self.input("dict").receive()
        if dict_p.isEOP():
            return False

        items = dict_p.value()
        dict_p.drop()

        self.output("keys").send(items.keys())
        self.output("values").send(items.values())

        return True


class DictIter(block.Block):
    def __init__(self):
        super(DictIter, self).__init__()

    def initialize(self):
        self.addInput(dict, "dict")
        self.addOutput(anytype.AnyType, "key")
        self.addOutput(anytype.AnyType, "value")
        self.addOutput(int, "length")

    def process(self):
        dict_p = self.input("dict").receive()
        if dict_p.isEOP():
            return False

        d = dict_p.value()
        dict_p.drop()

        self.output("length").send(len(d))
        for k, v in d.items():
            self.output("key").send(k)
            self.output("value").send(v)

        return True


class DictRemove(block.Block):
    def __init__(self):
        super(DictRemove, self).__init__()

    def initialize(self):
        self.addInput(dict, "inDict")
        self.addInput(anytype.AnyType, "key")
        self.addOutput(dict, "outDict")

    def process(self):
        in_dict_p = self.input("inDict").receive()
        if in_dict_p.isEOP():
            return False

        in_dict = in_dict_p.value()
        in_dict_p.drop()

        key_p = self.input("key").receive()
        if key_p.isEOP():
            return False

        key = key_p.value()
        key_p.drop()

        del in_dict[key]

        self.output("outDict").send(in_dict)

        return True


class DictUpdate(block.Block):
    def __init__(self):
        super(DictUpdate, self).__init__()

    def initialize(self):
        self.addInput(dict, "dictA")
        self.addInput(dict, "dictB")
        self.addOutput(dict, "output")

    def process(self):
        dict_a_p = self.input("dictA").receive()
        if dict_a_p.isEOP():
            return False

        dict_a = dict_a_p.value()
        dict_a_p.drop()

        dict_b_p = self.input("dictB").receive()
        if dict_b_p.isEOP():
            return False

        dict_b = dict_b_p.value()
        dict_b_p.drop()

        dict_a.update(dict_b)

        self.output("output").send(dict_a)

        return True
