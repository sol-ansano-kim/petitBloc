import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import block
from petitBloc import box
from petitBloc import chain
from petitBloc import conditionalBox
from petitBloc import workerManager
import threading
import multiprocessing
import Queue
import time


class MakeNumbers(block.Block):
    def __init__(self, name="", parent=None):
        super(MakeNumbers, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addOutput(float)

    def process(self):
        for n in range(10):
            self.output(0).send(n)

        return False


class Dump(block.Block):
    def __init__(self, name="", parent=None):
        super(Dump, self).__init__(name=name, parent=parent)
        self.dmp = Queue.Queue()
        self.__process = False

    def useProcess(self, v):
        self.__process = v
        self.flush()

    def initialize(self):
        self.addInput(int)

    def run(self):
        super(Dump, self).run()

    def flush(self):
        if self.dmp:
            if not isinstance(self.dmp, Queue.Queue):
                self.dmp.close()

            del self.dmp

        if self.__process:
            self.dmp = multiprocessing.Queue()
        else:
            self.dmp = Queue.Queue()

    def process(self):
        in_i = self.input(0).receive()

        if in_i.isEOP():
            return False

        self.dmp.put(in_i.value())
        in_i.drop()

        return True


class PlusOne(block.Block):
    def __init__(self):
        super(PlusOne, self).__init__()

    def initialize(self):
        self.addInput(int, "in")
        self.addOutput(int, "out")

    def run(self):
        in_i = self.input("in")
        in_p = in_i.receive()
        if in_p.isEOP():
            return

        self.output("out").send(in_p.value())
        in_p.drop()


class MakeOne(block.Block):
    def __init__(self):
        super(MakeOne, self).__init__()

    def initialize(self):
        self.addOutput(int, "out")

    def run(self):
        self.output("out").send(1)


class Bool(block.Block):
    def __init__(self):
        super(Bool, self).__init__()

    def initialize(self):
        self.addOutput(bool, "signal")
        self.addParam(bool, "do", False)

    def run(self):
        self.output("signal").send(self.param("do").get())


class ConditionalTest(unittest.TestCase):
    def test_conditional(self):
        box1 = box.Box("global")
        box2 = conditionalBox.ConditionalBox("local")
        num = MakeNumbers()
        dmp = Dump()
        bl = Bool()
        box1.addBlock(box2)
        box1.addBlock(bl)
        box2.addBlock(num)
        box2.addBlock(dmp)
        self.assertIsNotNone(chain.Chain(bl.output(0), box2.input(0)))
        self.assertIsNotNone(chain.Chain(num.output(0), dmp.input(0)))

        schedules = box1.getSchedule()

        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, [])

        bl.param("do").set(True)
        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, range(10))

        workerManager.WorkerManager.SetUseProcess(True)
        dmp.useProcess(True)

        bl.param("do").set(False)
        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, [])

        dmp.flush()
        bl.param("do").set(True)
        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, range(10))

    def test_inOut(self):
        box1 = box.Box("global")
        box2 = conditionalBox.ConditionalBox("local")
        bl = Bool()
        make = MakeOne()
        dmp = Dump()
        plus = PlusOne()

        box1.addBlock(box2)
        box1.addBlock(bl)
        box1.addBlock(dmp)
        box1.addBlock(make)

        box2.addBlock(plus)
        workerManager.WorkerManager.SetUseProcess(False)
        in_p = box2.addInputProxy(int, "in")
        out_p = box2.addOutputProxy(int, "out")

        self.assertIsNotNone(chain.Chain(make.output(0), in_p[0]))
        self.assertIsNotNone(chain.Chain(in_p[1], plus.input(0)))
        self.assertIsNotNone(chain.Chain(plus.output(0), out_p[0]))
        self.assertIsNotNone(chain.Chain(out_p[1], dmp.input(0)))
        self.assertIsNotNone(chain.Chain(bl.output(0), box2.input(0)))

        schedules = box1.getSchedule()

        bl.param("do").set(False)
        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, [])

        dmp.flush()
        bl.param("do").set(True)
        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, [1])

        workerManager.WorkerManager.SetUseProcess(True)
        dmp.useProcess(True)

        bl.param("do").set(False)
        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, [])

        dmp.flush()
        bl.param("do").set(True)
        workerManager.WorkerManager.RunSchedule(schedules)
        results = []
        while (not dmp.dmp.empty()):
            results.append(dmp.dmp.get())
        self.assertEqual(results, [1])


if __name__ == "__main__":
    unittest.main()
