import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import box
from petitBloc import block
from petitBloc import chain
from petitBloc import workerManager


class Make(block.Block):
    def initialize(self):
        self.addOutput(float)

    def process(self):
        for i in range(100):
            self.output(0).send(i)
        return False


class Add(block.Block):
    def initialize(self):
        self.addInput(float)
        self.addOutput(float)
        self.addParam(float)

    def process(self):
        p = self.input(0).receive()
        if p.isEOP():
            return False

        sys.stdout.flush()
        self.output(0).send(p.value() + 1)
        return True


class Mult(block.Block):
    def initialize(self):
        self.addInput(float)
        self.addOutput(float)
        self.addParam(float)

    def process(self):
        p = self.input(0).receive()
        if p.isEOP():
            return False

        sys.stdout.flush()
        self.output(0).send(p.value() * 2)
        return True


class PatchTest(unittest.TestCase):
    def test_100_times(self):
        b = box.Box()
        m = Make()
        a = Add()
        mt = Mult()
        a.param(0).set(1.0)
        b.addBlock(m)
        b.addBlock(a)
        b.addBlock(mt)
        chain.Chain(m.output(0), a.input(0))
        chain.Chain(a.output(0), mt.input(0))

        s = b.getSchedule()
        workerManager.WorkerManager.SetUseProcess(True)
        for i in range(128):
            workerManager.WorkerManager.RunSchedule(s)


if __name__ == "__main__":
    unittest.main()
