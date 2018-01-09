import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import box
from petitBloc import block
from petitBloc import packet
from petitBloc import packet
import multiprocessing


class MakeNumbers(block.Block):
    def __init__(self, name="", parent=None):
        super(MakeNumbers, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addOutput(float)

    def run(self):
        for n in range(5):
            self.output().send(n)

        self.terminate()


class AddOne(block.Block):
    def __init__(self, name="", parent=None):
        super(AddOne, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)

    def run(self):
        while (True):
            in_f = self.input().receive()
            if in_f is packet.EndOfPacket:
                break
            self.output().send(in_f.value() + 1)
            in_f.drop()

        self.terminate()


class Mult(block.Block):
    def __init__(self, name="", parent=None):
        super(Mult, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)

    def run(self):
        while (True):
            in_f = self.input().receive()
            if in_f is packet.EndOfPacket:
                break
            self.output().send(in_f.value() * 1.1)
            in_f.drop()

        self.terminate()


class Dump(block.Block):
    def __init__(self, name="", parent=None):
        super(Dump, self).__init__(name=name, parent=parent)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(float)

    def run(self):
        while (True):
            in_f = self.input().receive()
            if in_f is packet.EndOfPacket:
                break
            self.dmp.put(in_f.value())
            in_f.drop()

        self.terminate()


class BoxTest(unittest.TestCase):
    def test_init(self):
        g = box.Box()
        self.assertIsNotNone(g)

    def test_add_bloc(self):
        g = box.Box()
        num = MakeNumbers(name="MakeNumber")
        dmp = Dump(name="Dump")

        g.addBlock(dmp)
        g.addBlock(num)

        last = num.output()
        aa = None
        for i in range(128):
            add = AddOne(name="AddOne{}".format(i))
            if i == 0:
                aa = add
            doub = Mult(name="Mult{}".format(i))
            g.addBlock(doub)
            g.addBlock(add)
            self.assertTrue(g.connect(last, add.input()))
            self.assertTrue(g.connect(add.output(), doub.input()))
            last = doub.output()

        self.assertTrue(g.connect(last, dmp.input()))
        v1 = []
        for i in range(5):
            for j in range(128):
                i += 1
                i *= 1.1
            v1.append(i)

        g.run()
        v2 = []
        while (not dmp.dmp.empty()):
            v2.append(dmp.dmp.get())

        self.assertEqual(v1, v2)


if __name__ == "__main__":
    unittest.main()
