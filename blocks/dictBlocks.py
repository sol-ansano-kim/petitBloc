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
        self.addInput(int, "groupBy", optional=True)
        self.addOutput(dict, "dict")

    def _exhaust_package(self, port, pkgtype=None):
        p = port.receive()
        while not p.isEOP():
            if pkgtype:
                v = p.value()
                self.warn("ToDict node '%s' dropped %s packet (%s)" % (self.name(), pkgtype, repr(v)))
            p.drop()
            p = port.receive()

    def run(self):
        gp = self.input("groupBy")
        kp = self.input("key")
        vp = self.input("value")

        hasgrp = gp.isConnected()
        count = None
        err = None

        grp_eop = False
        key_eop = False
        val_eop = False

        while not grp_eop:
            if hasgrp:
                grp_p = gp.receive()
                grp_eop = grp_p.isEOP()
                if not grp_eop:
                    count = grp_p.value()
                    if count < 0:
                        err = "Invalid packet count %d" % count
                        break
                    grp_p.drop()
                else:
                    count = 0
            else:
                grp_eop = True

            kc = 0
            vc = 0
            cur = 0
            output = {}

            while (count is None or cur < count) and not key_eop and not val_eop:
                key_p = kp.receive()
                key_eop = key_p.isEOP()
                if not key_eop:
                    key = key_p.value()
                    key_p.drop()
                    kc += 1

                val_p = vp.receive()
                val_eop = val_p.isEOP()
                if not val_eop:
                    val = val_p.value()
                    val_p.drop()
                    vc += 1

                if not key_eop and not val_eop:
                    output[key] = val
                else:
                    break

                cur += 1

            if kc != vc:
                err = "Key/Value count mismatch (got %d key(s), %d value(s))" % (kc, vc)
                break
            elif (count is not None and kc != count):
                err = "Not enough Key/Value pairs (got %d, expected %d)" % (kc, count)
                break
            elif count != 0:
                self.output("dict").send(output)

        if not grp_eop:
            self._exhaust_package(gp, pkgtype=(None if err else "groupBy"))

        if not key_eop:
            self._exhaust_package(kp, pkgtype=(None if err else "key"))

        if not val_eop:
            self._exhaust_package(vp, pkgtype=(None if err else "value"))

        if err:
            raise Exception(err)


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


class DictFormat(block.Block):
    def __init__(self):
        super(DictFormat, self).__init__()

    def initialize(self):
        self.addParam(str, "prefix", value="")
        self.addParam(str, "keyValueJoin", value="=")
        self.addParam(str, "itemPrefix", value="")
        self.addParam(str, "itemSuffix", value="")
        self.addParam(str, "itemJoin", value=", ")
        self.addParam(str, "suffix", value="")
        self.addInput(dict, "dict")
        self.addOutput(str, "output")

    def process(self):
        in_d = self.input("dict").receive()
        if in_d.isEOP():
            return False
        d = in_d.value()
        in_d.drop()

        pjn = self.param("keyValueJoin").get()
        ipf = self.param("itemPrefix").get()
        ijn = self.param("itemJoin").get()
        isf = self.param("itemSuffix").get()

        out = self.param("prefix").get()
        lst = []
        for k, v in d.items():
            lst.append(ipf + pjn.join(map(str, [k, v])) + isf)
        out += ijn.join(lst)
        out += self.param("suffix").get()

        self.output("output").send(out)

        return True
