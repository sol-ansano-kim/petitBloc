from petitBloc import block
import re


class StringAdd(block.Block):
    def __init__(self):
        super(StringAdd, self).__init__()

    def initialize(self):
        self.addInput(str, "string1")
        self.addInput(str, "string2")
        self.addOutput(str, "result")

    def run(self):
        self.__str1_eop = False
        self.__str2_eop = False
        self.__str1_dmp = None
        self.__str2_dmp = None
        super(StringAdd, self).run()

    def process(self):
        if not self.__str1_eop:
            in1 = self.input("string1").receive()
            if in1.isEOP():
                self.__str1_eop = True
            else:
                self.__str1_dmp = in1.value()
                in1.drop()

        if self.__str1_dmp is None:
            return False

        if not self.__str2_eop:
            in2 = self.input("string2").receive()
            if in2.isEOP():
                self.__str2_eop = True
            else:
                self.__str2_dmp = in2.value()
                in2.drop()

        if self.__str2_dmp is None:
            return False

        if self.__str1_eop and self.__str2_eop:
            return False

        self.output("result").send(self.__str1_dmp + self.__str2_dmp)

        return True


class StringReplace(block.Block):
    def __init__(self):
        super(StringReplace, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "old")
        self.addInput(str, "new")
        self.addOutput(str, "result")

    def run(self):
        self.__old_eop = False
        self.__new_eop = False
        self.__old_dmp = None
        self.__new_dmp = None
        super(StringReplace, self).run()

    def process(self):
        in1 = self.input("string").receive()
        if in1.isEOP():
            return False

        v1 = in1.value()
        in1.drop()

        if not self.__old_eop:
            in2 = self.input("old").receive()
            if in2.isEOP():
                self.__old_eop = True
            else:
                self.__old_dmp = in2.value()
                in2.drop()

        if self.__old_dmp is None:
            return False

        if not self.__new_eop:
            in3 = self.input("new").receive()
            if in3.isEOP():
                self.__new_eop = True
            else:
                self.__new_dmp = in3.value()
                in3.drop()

        if self.__new_dmp is None:
            return False

        self.output("result").send(v1.replace(self.__old_dmp, self.__new_dmp))

        return True


class StringCount(block.Block):
    def __init__(self):
        super(StringCount, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "substring")
        self.addOutput(int, "result")

    def run(self):
        self.__sub_eop = False
        self.__sub_dmp = None
        super(StringCount, self).run()

    def process(self):
        in1 = self.input("string").receive()
        if in1.isEOP():
            return False

        v1 = in1.value()
        in1.drop()

        if not self.__sub_eop:
            in2 = self.input("substring").receive()
            if in2.isEOP():
                self.__sub_eop = True
            else:
                self.__sub_dmp = in2.value()
                in2.drop()

        if self.__sub_dmp is None:
            return False

        self.output("result").send(v1.count(self.__sub_dmp))

        return True


class RegexFindAll(block.Block):
    def __init__(self):
        super(RegexFindAll, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addOutput(str, "result")

    def run(self):
        self.__pattern_eop = False
        self.__pattern_dmp = None
        super(RegexFindAll, self).run()

    def process(self):
        in1 = self.input("string").receive()
        if in1.isEOP():
            return False

        v1 = in1.value()
        in1.drop()

        if not self.__pattern_eop:
            in2 = self.input("pattern").receive()
            if in2.isEOP():
                self.__pattern_eop = True
            else:
                self.__pattern_dmp = in2.value()
                in2.drop()

        if self.__pattern_dmp is None:
            return False

        for r in re.findall(self.__pattern_dmp, v1):
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

    def run(self):
        self.__pattern_eop = False
        self.__pattern_dmp = None
        self.__replace_eop = False
        self.__replace_dmp = None
        super(RegexSub, self).run()

    def process(self):
        in1 = self.input("string").receive()
        if in1.isEOP():
            return False

        v1 = in1.value()
        in1.drop()

        if not self.__pattern_eop:
            in2 = self.input("pattern").receive()
            if in2.isEOP():
                self.__pattern_eop = True
            else:
                self.__pattern_dmp = in2.value()
                in2.drop()

        if self.__pattern_dmp is None:
            return False

        if not self.__replace_eop:
            in2 = self.input("replace").receive()
            if in2.isEOP():
                self.__replace_eop = True
            else:
                self.__replace_dmp = in2.value()
                in2.drop()

        if self.__replace_dmp is None:
            return False

        self.output("result").send(re.sub(self.__pattern_dmp, self.__replace_dmp, v1))

        return True


class RegexSelector(block.Block):
    def __init__(self):
        super(RegexSelector, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addOutput(str, "matched")
        self.addOutput(str, "unmatched")

    def run(self):
        self.__pattern_eop = False
        self.__pattern_dmp = None
        super(RegexSelector, self).run()

    def process(self):
        in1 = self.input("string").receive()
        if in1.isEOP():
            return False

        v1 = in1.value()
        in1.drop()

        if not self.__pattern_eop:
            in2 = self.input("pattern").receive()
            if in2.isEOP():
                self.__pattern_eop = True
            else:
                self.__pattern_dmp = in2.value()
                in2.drop()

        if self.__pattern_dmp is None:
            return False

        if re.search(self.__pattern_dmp, v1):
            self.output("matched").send(v1)
        else:
            self.output("unmatched").send(v1)

        return True


class RegexSearch(block.Block):
    def __init__(self):
        super(RegexSearch, self).__init__()

    def initialize(self):
        self.addInput(str, "string")
        self.addInput(str, "pattern")
        self.addOutput(str, "result")

    def run(self):
        self.__pattern_eop = False
        self.__pattern_dmp = None
        super(RegexSearch, self).run()

    def process(self):
        in1 = self.input("string").receive()
        if in1.isEOP():
            return False

        v1 = in1.value()
        in1.drop()

        if not self.__pattern_eop:
            in2 = self.input("pattern").receive()
            if in2.isEOP():
                self.__pattern_eop = True
            else:
                self.__pattern_dmp = in2.value()
                in2.drop()

        if self.__pattern_dmp is None:
            return False

        res = re.search(self.__pattern_dmp, v1)
        if not res:
            self.output("result").send("")

            return True

        self.output("result").send(v1[res.start():res.end()])
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
