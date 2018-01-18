import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import block
from petitBloc import box
from petitBloc import port
from petitBloc import chain
from petitBloc import workerManager
import time


class MakeNumbers(block.Block):
    def __init__(self, name="", parent=None):
        super(MakeNumbers, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addOutput(int)
        self.addParam(int, "start", 0)
        self.addParam(int, "stop", 10)
        self.addParam(int, "step", 1)

    def run(self):
        start = self.param("start").get()
        stop = self.param("stop").get()
        step = self.param("step").get()
        if step < 1:
            step = 1

        for n in range(start, stop, step):
            self.output(0).send(n)


class RaiseError(block.Block):
    def __init__(self, name="", parent=None):
        super(RaiseError, self).__init__(name=name, parent=parent)

    def initialize(self):
        self.addInput(int)
        self.addParam(int, "value", 0)

    def process(self):
        in_f = self.input(0).receive()
        if in_f.isEOP():
            return False

        if in_f.value() == self.param(0).get():
            raise Exception, "Test Error at : {}".format(in_f.value())

        in_f.drop()

        return True


class LoggingTest(unittest.TestCase):
    def test_packetInfo(self):
        src_port = port.OutPort(int)
        dst_port = port.InPort(int)

        chan = chain.Chain(src_port, dst_port)
        src_port.activate()
        dst_port.activate()
        src_port.send(1)
        time.sleep(0.1)
        src_port.send(2)
        time.sleep(0.1)
        dst_port.receive()
        time.sleep(0.1)
        src_port.terminate()
        dst_port.terminate()

        self.assertEqual(src_port.packetInfo(), [1, 2])
        self.assertEqual(dst_port.packetInfo(), [1])
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)

    def test_error(self):
        b = box.Box()
        m = MakeNumbers()
        e = RaiseError()
        b.addBlock(m)
        b.addBlock(e)
        e.param("value").set(5)
        b.connect(m.output(0), e.input(0))
        workerManager.WorkerManager.RunSchedule(b.getSchedule())
        self.assertTrue(e.isFailed())
        self.assertFalse(e.isTerminated())

        
if __name__ == "__main__":
    unittest.main()
