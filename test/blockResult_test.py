import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import block
from petitBloc import chain
from petitBloc import box
from petitBloc import const
from petitBloc import workerManager
import threading
import multiprocessing
import Queue
import time


class RaiseError(block.Block):
    def __init__(self):
        super(RaiseError, self).__init__()

    def initialize(self):
        self.addParam(bool, "error", False)

    def run(self):
        if self.param("error").get():
            raise Exception, "TEST!"


class Dump(block.Block):
    def __init__(self, name="", parent=None):
        super(Dump, self).__init__(name=name, parent=parent)
        self.dmp = Queue.Queue()
        self.__process = False

    def useProcess(self, v):
        self.__process = v
        self.flush()

    def initialize(self):
        self.addInput(bool)

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
        in_b = self.input(0).receive()
        if in_b.isEOP():
            return False

        self.dmp.put(in_b.value())
        in_b.drop()

        return True


class TestBlockResult(unittest.TestCase):
    def test(self):
        b = box.Box()
        dmp = Dump()
        r = RaiseError()
        b.addBlock(dmp)
        b.addBlock(r)

        self.assertIsNotNone(chain.Chain(r.output("success"), dmp.input(0)))

        schedule = b.getSchedule()

        workerManager.WorkerManager.SetLogLevel(const.LogLevel.NoLog)
        workerManager.WorkerManager.SetUseProcess(False)

        for i in range(5):
            dmp.flush()
            workerManager.WorkerManager.RunSchedule(schedule)
            results = []
            while (not dmp.dmp.empty()):
                results.append(dmp.dmp.get())
            self.assertEqual(results, [True])

        r.param("error").set(True)

        for i in range(5):
            dmp.flush()
            workerManager.WorkerManager.RunSchedule(schedule)
            results = []
            while (not dmp.dmp.empty()):
                results.append(dmp.dmp.get())
            self.assertEqual(results, [False])

        workerManager.WorkerManager.SetUseProcess(True)
        r.param("error").set(False)
        dmp.useProcess(True)
        for i in range(5):
            dmp.flush()
            workerManager.WorkerManager.RunSchedule(schedule)
            results = []
            while (not dmp.dmp.empty()):
                results.append(dmp.dmp.get())
            self.assertEqual(results, [True])

        r.param("error").set(True)

        for i in range(5):
            dmp.flush()
            workerManager.WorkerManager.RunSchedule(schedule)
            results = []
            while (not dmp.dmp.empty()):
                results.append(dmp.dmp.get())
            self.assertEqual(results, [False])


if __name__ == "__main__":
    unittest.main()
