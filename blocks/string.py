from petitBloc import block
import re


class StringAdd(block.Block):
    def __init__(self):
        super(StringAdd, self).__init__()

    def initialize(self):
        self.addInput(str, "string1")
        self.addInput(str, "string2")
        self.addOutput(str, "result")

    def process(self):
        v1 = None
        v2 = None

        in1 = self.input("string1").receive()
        in2 = self.input("string2").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if v1 is None or v2 is None:
            return False

        self.output("result").send(v1 + v2)

        return True


class StringReplace(block.Block):
    def __init__(self):
        super(StringReplace, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "old")
        self.addInput(str, "new")
        self.addOutput(str, "result")

    def process(self):
        v1 = None
        v2 = None
        v3 = None

        in1 = self.input("string").receive()
        in2 = self.input("old").receive()
        in3 = self.input("new").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if not in3.isEOP():
            v3 = in3.value()
            in3.drop()

        if v1 is None or v2 is None or v3 is None:
            return False

        self.output("result").send(v1.replace(v2, v3))

        return True


class StringCount(block.Block):
    def __init__(self):
        super(StringCount, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "substring")
        self.addOutput(int, "result")

    def process(self):
        v1 = None
        v2 = None

        in1 = self.input("string").receive()
        in2 = self.input("substring").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if v1 is None or v2 is None:
            return False

        self.output("result").send(v1.count(v2))

        return True


class RegexFindAll(block.Block):
    def __init__(self):
        super(RegexFindAll, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addOutput(str, "result")

    def process(self):
        v1 = None
        v2 = None

        in1 = self.input("string").receive()
        in2 = self.input("pattern").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if v1 is None or v2 is None:
            return False

        for r in re.findall(v2, v1):
            self.output("result").send(r)

        return True


class RegexSub(block.Block):
    def __init__(self):
        super(RegexSub, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addInput(str, "replace")
        self.addOutput(str, "result")

    def process(self):
        v1 = None
        v2 = None
        v3 = None

        in1 = self.input("string").receive()
        in2 = self.input("pattern").receive()
        in3 = self.input("replace").receive()

        if not in1.isEOP():
            v1 = in1.value()
            in1.drop()

        if not in2.isEOP():
            v2 = in2.value()
            in2.drop()

        if not in3.isEOP():
            v3 = in3.value()
            in3.drop()

        if v1 is None or v2 is None or v3 is None:
            return False

        self.output("result").send(re.sub(v2, v3, v1))

        return True
