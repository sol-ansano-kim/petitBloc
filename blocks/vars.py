from petitBloc import block


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
