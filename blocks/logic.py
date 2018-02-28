from petitBloc import block


class BoolSelector(block.Block):
    def __init__(self):
        super(BoolSelector, self).__init__()

    def initialize(self):
        self.addInput(bool, "value")
        self.addInput(bool, "condition")
        self.addOutput(bool, "matched")
        self.addOutput(bool, "unmatched")

    def process(self):
        val_p = self.input("value").receive()
        if val_p.isEOP():
            return False

        val = val_p.value()
        val_p.drop()

        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        if con:
            self.output("matched").send(val)

        else:
            self.output("unmatched").send(val)

        return True


class IntSelector(block.Block):
    def __init__(self):
        super(IntSelector, self).__init__()

    def initialize(self):
        self.addInput(int, "value")
        self.addInput(bool, "condition")
        self.addOutput(int, "matched")
        self.addOutput(int, "unmatched")

    def process(self):
        val_p = self.input("value").receive()
        if val_p.isEOP():
            return False

        val = val_p.value()
        val_p.drop()

        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        if con:
            self.output("matched").send(val)

        else:
            self.output("unmatched").send(val)

        return True


class FloatSelector(block.Block):
    def __init__(self):
        super(FloatSelector, self).__init__()

    def initialize(self):
        self.addInput(float, "value")
        self.addInput(bool, "condition")
        self.addOutput(float, "matched")
        self.addOutput(float, "unmatched")

    def process(self):
        val_p = self.input("value").receive()
        if val_p.isEOP():
            return False

        val = val_p.value()
        val_p.drop()

        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        if con:
            self.output("matched").send(val)

        else:
            self.output("unmatched").send(val)

        return True


class StringSelector(block.Block):
    def __init__(self):
        super(StringSelector, self).__init__()

    def initialize(self):
        self.addInput(str, "value")
        self.addInput(bool, "condition")
        self.addOutput(str, "matched")
        self.addOutput(str, "unmatched")

    def process(self):
        val_p = self.input("value").receive()
        if val_p.isEOP():
            return False

        val = val_p.value()
        val_p.drop()

        con_p = self.input("condition").receive()
        if con_p.isEOP():
            return False

        con = con_p.value()
        con_p.drop()

        if con:
            self.output("matched").send(val)

        else:
            self.output("unmatched").send(val)

        return True
