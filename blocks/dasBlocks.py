from petitBloc import block
from petitBloc import anytype
from petitBloc import dastype
import das
import das.cli


class DasRead(block.Block):
    def __init__(self):
        super(DasRead, self).__init__()

    def initialize(self):
        self.addInput(str, "filepath")
        self.addOutput(dastype.DasTypeBase, "dasObj")

    def process(self):
        fp = self.input("filepath").receive()
        if fp.isEOP():
            return False

        fv = fp.value()
        fp.drop()

        das_obj = das.read(fv)
        self.output("dasObj").send(das_obj)

        return True


class DasWrite(block.Block):
    def __init__(self):
        super(DasWrite, self).__init__()

    def initialize(self):
        self.addInput(dastype.DasTypeBase, "dasObj")
        self.addInput(str, "filepath")

    def process(self):
        fp = self.input("filepath").receive()
        if fp.isEOP():
            return False

        fv = fp.value()
        fp.drop()

        dp = self.input("dasObj").receive()
        if dp.isEOP():
            return False

        dv = dp.value()
        dp.drop()

        das.write(dv, fv)

        return True


class DasGet(block.Block):
    def __init__(self):
        super(DasGet, self).__init__()

    def initialize(self):
        self.addInput(dastype.DasTypeBase, "dasObj")
        self.addInput(str, "key")
        self.addOutput(anytype.AnyType, "output")

    def process(self):
        dp = self.input("dasObj").receive()
        if dp.isEOP():
            return False

        dv = dp.value()
        dp.drop()

        kp = self.input("key").receive()
        if kp.isEOP():
            return False

        kv = kp.value()
        kp.drop()

        self.output("output").send(das.cli.get(dv, kv))

        return True


class DasSet(block.Block):
    def __init__(self):
        super(DasSet, self).__init__()

    def initialize(self):
        self.addInput(dastype.DasTypeBase, "inDasObj")
        self.addInput(str, "key")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(anytype.AnyType, "outDasObj")

    def process(self):
        dp = self.input("inDasObj").receive()
        if dp.isEOP():
            return False

        dv = das.copy(dp.value())
        dp.drop()

        kp = self.input("key").receive()
        if kp.isEOP():
            return False

        kv = kp.value()
        kp.drop()

        vp = self.input("value").receive()
        if vp.isEOP():
            return False

        vv = vp.value()
        vp.drop()

        das.cli.set(dv, kv, str(vv))

        self.output("outDasObj").send(dv)

        return True


class DasEval(block.Block):
    def __init__(self):
        super(DasEval, self).__init__()

    def initialize(self):
        self.addInput(dastype.DasTypeBase, "inDasObj")
        self.addInput(str, "expression")
        self.addOutput(anytype.AnyType, "output")
        self.addOutput(anytype.AnyType, "outDasObj")

    def process(self):
        dp = self.input("inDasObj").receive()
        if dp.isEOP():
            return False

        dv = das.copy(dp.value())
        dp.drop()

        ep = self.input("expression").receive()
        if ep.isEOP():
            return False

        ev = ep.value()
        ep.drop()

        res = das.cli.eval(dv, ev)
        self.output("output").send(res)
        self.output("outDasObj").send(dv)

        return True


class DasNew(block.Block):
    def __init__(self):
        super(DasNew, self).__init__()

    def initialize(self):
        self.addParam(bool, "specifyFields")
        self.addInput(str, "schemaType")
        self.addInput(dict, "fields")
        self.addOutput(anytype.AnyType, "dasObj")

    def process(self):
        st = self.input("schemaType").receive()
        if st.isEOP():
            return False

        if not self.param("specifyFields").get():
            fd = {}
        else:
            _fd = self.input("fields").receive()
            if _fd.isEOP():
                return False

            fd = _fd.value()
            _fd.drop()

        rv = das.make(st.value(), **fd)

        st.drop()

        self.output("dasObj").send(rv)

        return True


class DasAdd(block.Block):
    def __init__(self):
        super(DasAdd, self).__init__()

    def initialize(self):
        self.addInput(dastype.DasTypeBase, "inDasObj")
        self.addInput(str, "key")
        self.addInput(anytype.AnyType, "value")
        self.addOutput(anytype.AnyType, "outDasObj")

    def process(self):
        dp = self.input("inDasObj").receive()
        if dp.isEOP():
            return False

        dv = das.copy(dp.value())
        dp.drop()

        kp = self.input("key").receive()
        if kp.isEOP():
            return False

        kv = kp.value()
        kp.drop()

        vp = self.input("value").receive()
        if vp.isEOP():
            return False

        vv = vp.value()
        vp.drop()

        das.cli.add(dv, kv, str(vv))
        self.output("outDasObj").send(dv)

        return True


class DasValidate(block.Block):
    def __init__(self):
        super(DasValidate, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "value")
        self.addInput(str, "schema")
        self.addOutput(anytype.AnyType, "output")

    def process(self):
        dp = self.input("value").receive()
        if dp.isEOP():
            return False

        dv = dp.value()
        dp.drop()

        sp = self.input("schema").receive()
        if sp.isEOP():
            return False

        sv = sp.value()
        sp.drop()

        self.output("output").send(das.validate(dv, sv))

        return True
