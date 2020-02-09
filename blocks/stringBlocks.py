from petitBloc import block
from petitBloc import anytype
import re


class StringAdd(block.Block):
    def __init__(self):
        super(StringAdd, self).__init__()

    def initialize(self):
        self.addInput(str, "string1")
        self.addInput(str, "string2")
        self.addOutput(str, "output")

    def process(self):
        s1_p = self.input("string1").receive()
        if s1_p.isEOP():
            return False

        s1 = s1_p.value()
        s1_p.drop()

        s2_p = self.input("string2").receive()
        if s2_p.isEOP():
            return False

        s2 = s2_p.value()
        s2_p.drop()

        self.output("output").send(s1 + s2)

        return True


class StringReplace(block.Block):
    def __init__(self):
        super(StringReplace, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "old")
        self.addInput(str, "new")
        self.addOutput(str, "output")

    def process(self):
        string_p = self.input("string").receive()
        if string_p.isEOP():
            return False

        string = string_p.value()
        string_p.drop()

        old_p = self.input("old").receive()
        if old_p.isEOP():
            return False

        old = old_p.value()
        old_p.drop()

        new_p = self.input("new").receive()
        if new_p.isEOP():
            return False

        new = new_p.value()
        new_p.drop()

        self.output("output").send(string.replace(old, new))

        return True


class StringCount(block.Block):
    def __init__(self):
        super(StringCount, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "substring")
        self.addOutput(int, "output")

    def process(self):
        string_p = self.input("string").receive()
        if string_p.isEOP():
            return False

        string = string_p.value()
        string_p.drop()

        sub_p = self.input("substring").receive()
        if sub_p.isEOP():
            return False

        sub = sub_p.value()
        sub_p.drop()

        self.output("output").send(string.count(sub))

        return True


class StringSplit(block.Block):
    def __init__(self):
        super(StringSplit, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "substring")
        self.addOutput(list, "output")

    def process(self):
        string_p = self.input("string").receive()
        if string_p.isEOP():
            return False

        string = string_p.value()
        string_p.drop()

        sub_p = self.input("substring").receive()
        if sub_p.isEOP():
            return False

        sub = sub_p.value()
        sub_p.drop()

        self.output("output").send(string.split(sub))

        return True


class StringJoin(block.Block):
    def __init__(self):
        super(StringJoin, self).__init__()

    def initialize(self):
        self.addInput(list, "strings")
        self.addInput(str, "joiner")
        self.addOutput(str, "output")

    def process(self):
        strings_p = self.input("strings").receive()
        if strings_p.isEOP():
            return False

        sl = strings_p.value()
        strings_p.drop()

        joiner_p = self.input("joiner").receive()
        if joiner_p.isEOP():
            return False

        j = joiner_p.value()
        joiner_p.drop()

        self.output("output").send(j.join(sl))

        return True


class RegexFindAll(block.Block):
    def __init__(self):
        super(RegexFindAll, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addOutput(str, "output")

    def process(self):
        string_p = self.input("string").receive()
        if string_p.isEOP():
            return False

        string = string_p.value()
        string_p.drop()

        pat_p = self.input("pattern").receive()
        if pat_p.isEOP():
            return False

        pat = pat_p.value()
        pat_p.drop()

        for r in re.findall(pat, string):
            self.output("output").send(r)

        return True


class RegexSub(block.Block):
    def __init__(self):
        super(RegexSub, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addInput(str, "replace")
        self.addOutput(str, "output")

    def process(self):
        string_p = self.input("string").receive()
        if string_p.isEOP():
            return False

        string = string_p.value()
        string_p.drop()

        pat_p = self.input("pattern").receive()
        if pat_p.isEOP():
            return False

        pat = pat_p.value()
        pat_p.drop()

        rep_p = self.input("replace").receive()
        if rep_p.isEOP():
            return False

        rep = rep_p.value()
        rep_p.drop()

        self.output("output").send(re.sub(pat, rep, string))

        return True


class RegexSelect(block.Block):
    def __init__(self):
        super(RegexSelect, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addOutput(str, "matched")
        self.addOutput(str, "unmatched")

    def process(self):
        string_p = self.input("string").receive()
        if string_p.isEOP():
            return False

        string = string_p.value()
        string_p.drop()

        pat_p = self.input("pattern").receive()
        if pat_p.isEOP():
            return False

        pat = pat_p.value()
        pat_p.drop()

        if re.search(pat, string):
            self.output("matched").send(string)
        else:
            self.output("unmatched").send(string)

        return True


class RegexSelector(RegexSelect):
    def __init__(self):
        super(RegexSelector, self).__init__()

    def run(self):
        self.warn("'RegexSelector' block is deprecated. Please use 'RegexSelect' instead")
        super(RegexSelector, self).run()


class RegexSearch(block.Block):
    def __init__(self):
        super(RegexSearch, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addOutput(str, "output")

    def process(self):
        string_p = self.input("string").receive()
        if string_p.isEOP():
            return False

        string = string_p.value()
        string_p.drop()

        pat_p = self.input("pattern").receive()
        if pat_p.isEOP():
            return False

        pat = pat_p.value()
        pat_p.drop()

        res = re.search(pat, string)
        if not res:
            self.output("output").send("")

            return True

        self.output("output").send(string[res.start():res.end()])

        return True


class ToString(block.Block):
    def __init__(self):
        super(ToString, self).__init__()

    def initialize(self):
        self.addInput(anytype.AnyType, "value")
        self.addOutput(str, "string")

    def process(self):
        val_p = self.input("value").receive()
        if val_p.isEOP():
            return False

        self.output("string").send(str(val_p.value()))
        val_p.drop()

        return True


class FloatToString(block.Block):
    def __init__(self):
        super(FloatToString, self).__init__()

    def initialize(self):
        self.addParam(int, "demical", value=3)
        self.addInput(float, "float")
        self.addOutput(str, "string")

    def process(self):
        demi = self.param("demical").get()
        demi = 1 if demi < 1 else demi
        in_p = self.input("float").receive()

        if in_p.isEOP():
            return False

        v = in_p.value()
        in_p.drop()

        self.output("string").send("{0:.{demi}g}".format(v, demi=demi))

        return True


class StringToFloat(block.Block):
    def __init__(self):
        super(StringToFloat, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addOutput(float, "float")

    def process(self):
        in_p = self.input("string").receive()

        if in_p.isEOP():
            return False

        v = in_p.value()
        in_p.drop()

        self.output("float").send(float(v))

        return True


class StringLength(block.Block):
    def __init__(self):
        super(StringLength, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addOutput(int, "length")

    def process(self):
        in_p = self.input("string").receive()

        if in_p.isEOP():
            return False

        self.output("length").send(len(in_p.value()))
        in_p.drop()

        return True


class StringEval(block.Block):
    def __init__(self):
        super(StringEval, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addOutput(anytype.AnyType, "output")

    def process(self):
        in_p = self.input("string").receive()

        if in_p.isEOP():
            return False

        self.output("output").send(eval(in_p.value()))

        in_p.drop()

        return True
