import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import box
from petitBloc import block
from petitBloc import manager
import multiprocessing


class MakeNumbers(block.Block):
    def __init__(self, name="", parent=None):
        super(MakeNumbers, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addOutput(float)

    def run(self):
        for n in range(100):
            self.output().send(n)


class AddOne(block.Block):
    def __init__(self, name="", parent=None):
        super(AddOne, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(int)
        self.addOutput(int)

    def run(self):
        while (True):
            in_f = self.input().receive()
            if in_f.isEOP():
                break
            self.output().send(in_f.value() + 1)
            in_f.drop()


class Mult(block.Block):
    def __init__(self, name="", parent=None):
        super(Mult, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)

    def run(self):
        while (True):
            in_f = self.input().receive()
            if in_f.isEOP():
                break
            self.output().send(in_f.value() * 1.1)
            in_f.drop()


class Dump(block.Block):
    def __init__(self, name="", parent=None):
        super(Dump, self).__init__(name=name, parent=parent)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(float)

    def run(self):
        while (True):
            in_f = self.input().receive()
            if in_f.isEOP():
                break
            self.dmp.put(in_f.value())
            in_f.drop()


class BoxTest(unittest.TestCase):
    def test_init(self):
        g = box.Box()
        self.assertIsNotNone(g)

    def test_add_bloc(self):
        g = box.Box()
        num = MakeNumbers(name="MakeNumber")
        dmp = Dump(name="Dump")

        self.assertTrue(g.addBlock(dmp))
        self.assertTrue(g.addBlock(num))

        last = num.output()
        aa = None
        for i in range(100):
            add = AddOne(name="AddOne{}".format(i))
            if i == 0:
                aa = add
            doub = Mult(name="Mult{}".format(i))
            self.assertTrue(g.addBlock(doub))
            self.assertTrue(g.addBlock(add))
            self.assertTrue(g.connect(last, add.input()))
            self.assertTrue(g.connect(add.output(), doub.input()))
            last = doub.output()

        self.assertTrue(g.connect(last, dmp.input()))

        v1 = []
        for i in range(100):
            for j in range(100):
                i = int(i + 1)
                i *= 1.1
            v1.append(i)

        schedule = g.getSchedule()
        manager.RunSchedule(schedule)

        v2 = []
        while (not dmp.dmp.empty()):
            v2.append(dmp.dmp.get())

        self.assertEqual(v1, v2)

    def test_subnet(self):
        g = box.Box()

        num1 = MakeNumbers(name="OutsideNum")
        dmp1 = Dump(name="OutSideDmp")
        self.assertTrue(g.addBlock(num1))
        self.assertTrue(g.addBlock(dmp1))
        self.assertTrue(g.connect(num1.output(), dmp1.input()))

        c = box.Box()
        self.assertTrue(g.addBlock(c))
        num2 = MakeNumbers(name="InsideNum")
        add = AddOne("InsideAdd")
        dmp2 = Dump(name="InSideDmp")
        self.assertTrue(c.addBlock(num2))
        self.assertTrue(c.addBlock(dmp2))
        self.assertTrue(c.addBlock(add))
        self.assertTrue(c.connect(num2.output(), add.input()))
        self.assertTrue(c.connect(add.output(), dmp2.input()))

        manager.RunSchedule(g.getSchedule())

        out_dmp = []
        out_value = []
        in_dmp = []
        in_value = []

        for i in range(100):
            out_value.append(float(i))
            in_value.append(int(i + 1))

        while (not dmp1.dmp.empty()):
            out_dmp.append(dmp1.dmp.get())

        while (not dmp2.dmp.empty()):
            in_dmp.append(dmp2.dmp.get())

        self.assertEqual(out_dmp, out_value)
        self.assertEqual(in_dmp, in_value)


if __name__ == "__main__":
    unittest.main()
