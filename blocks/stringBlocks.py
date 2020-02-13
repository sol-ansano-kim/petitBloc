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
        self.addOutput(str, "output")
        self.addOutput(list, "outList")

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

        op = self.output("output")
        out_list = string.split(sub)
        for s in out_list:
            op.send(s)

        self.output("outList").send(out_list)

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
        self.addOutput(list, "outList")

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

        out_list = re.findall(pat, string)
        for r in out_list:
            self.output("output").send(r)

        self.output("outList").send(out_list)

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


class RegexFork(block.Block):
    def __init__(self):
        super(RegexFork, self).__init__()

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


class StringFormat(block.Block):
    def __init__(self):
        super(StringFormat, self).__init__()

    def initialize(self):
        self.addParam(str, "formatString")
        self.addEnumParam("formatSyntax", ["printf", "python"], value=0)
        self.addInput(anytype.AnyType, "value")
        self.addOutput(str, "string")

    def process(self):
        fmt = self.param("formatString").get()
        syn = self.param("formatSyntax").get()

        val_p = self.input("value").receive()
        if val_p.isEOP():
            return False
        val = val_p.value()
        val_p.drop()

        if syn == 0:
            ret = fmt % val
        else:
            ret = fmt.format(val)

        self.output("string").send(ret)

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

    def run(self):
        self.warn("FloatToString is deprecated, use StringFormat instead")
        super(FloatToString, self).run()


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

    def run(self):
        self.warn("StringToFloat is deprecated, use ToFloat instead")
        super(StringToFloat, self).run()


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


class StringIsEmpty(block.Block):
    def __init__(self):
        super(StringIsEmpty, self).__init__()

    def initialize(self):
        self.addParam(bool, "invert", value=False)
        self.addInput(str, "string")
        self.addOutput(bool, "empty")

    def process(self):
        in_p = self.input("string").receive()

        if in_p.isEOP():
            return False

        empty = (len(in_p.value()) == 0)
        in_p.drop()

        invert = self.param("invert").get()

        self.output("empty").send(empty if not invert else not empty)

        return True


class StringCompare(block.Block):
    def __init__(self):
        super(StringCompare, self).__init__()

    def initialize(self):
        self.addParam(bool, "caseSensitive", value=True)
        self.addParam(bool, "invert", value=False)
        self.addInput(str, "string1")
        self.addInput(str, "string2")
        self.addOutput(bool, "same")

    def process(self):
        in_s1 = self.input("string1").receive()

        if in_s1.isEOP():
            return False

        s1 = in_s1.value()
        in_s1.drop()

        in_s2 = self.input("string2").receive()

        if in_s2.isEOP():
            return False

        s2 = in_s2.value()
        in_s2.drop()

        caseSensitive = self.param("caseSensitive").get()
        if not caseSensitive:
            s1 = s1.lower()
            s2 = s2.lower()

        invert = self.param("invert").get()

        self.output("same").send(s1 == s2 if not invert else s1 != s2)

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


class StringStrip(block.Block):
    def __init__(self):
        super(StringStrip, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addEnumParam("where", ["left", "right", "both"], value=2)
        self.addOutput(str, "output")

    def process(self):
        in_p = self.input("string").receive()

        if in_p.isEOP():
            return False

        s = in_p.value()
        in_p.drop()

        where = self.param("where").get()
        if where <= 0:
            s = s.lstrip()
        elif where == 1:
            s = s.rstrip()
        else:
            s = s.strip()

        self.output("output").send(s)

        return True
