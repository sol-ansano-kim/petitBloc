from petitBloc import block
import re


class Int(block.Block):
    def __init__(self):
        super(Int, self).__init__()

    def initialize(self):
        self.addParam(int, "value")
        self.addOutput(int, "value")

    def run(self):
        self.output("value").send(self.param("value").get())


class Float(block.Block):
    def __init__(self):
        super(Float, self).__init__()

    def initialize(self):
        self.addParam(float, "value")
        self.addOutput(float, "value")

    def run(self):
        self.output("value").send(self.param("value").get())


class Boolean(block.Block):
    def __init__(self):
        super(Boolean, self).__init__()

    def initialize(self):
        self.addParam(bool, "value")
        self.addOutput(bool, "value")

    def run(self):
        self.output("value").send(self.param("value").get())


class String(block.Block):
    def __init__(self):
        super(String, self).__init__()

    def initialize(self):
        self.addParam(str, "value")
        self.addOutput(str, "value")

    def run(self):
        self.output("value").send(self.param("value").get())


class ContextDict(block.Block):
    def __init__(self):
        super(ContextDict, self).__init__()

    def initialize(self):
        self.addParam(str, "fields")
        self.addOutput(dict, "dict")

    def run(self):
        fields = self.param("fields").get()
        keys = re.split(r"[\s,:;]+", fields)
        out = {}
        ctx = self.ancestor().getContext()
        for k in keys:
            v = ctx.get(k, None)
            if v is not None:
                out[k] = v
        self.output("dict").send(out)
