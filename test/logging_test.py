import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import block
from petitBloc import box
from petitBloc import port
from petitBloc import chain
from petitBloc import workerManager
from petitBloc import const
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
        self.debug("MakeNumbers start")
        start = self.param("start").get()
        stop = self.param("stop").get()
        step = self.param("step").get()
        if step < 1:
            step = 1
        self.debug("start : {} stop : {} step : {}".format(start, stop, step))
        for n in range(start, stop, step):
            self.output(0).send(n)
            self.debug("send value {}".format(str(n)))
        self.warn("testing")
        self.debug("MakeNumbers end")


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

        self.debug("receive value {}".format(str(in_f.value())))

        if in_f.value() == self.param(0).get():
            self.error("raise error!")
            raise Exception, "Test Error at : {}".format(in_f.value())

        in_f.drop()

        return True


class LoggingTest(unittest.TestCase):
    def test_packetHistory(self):
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

        self.assertEqual(src_port.packetHistory(), [1, 2])
        self.assertEqual(dst_port.packetHistory(), [1])
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)

    def test_error(self):
        workerManager.WorkerManager.SetUseProcess(False)
        workerManager.WorkerManager.SetLogLevel(const.LogLevel.NoLog)
        b = box.Box()
        m = MakeNumbers()
        e = RaiseError()
        b.addBlock(m)
        b.addBlock(e)
        e.param("value").set(5)
        chain.Chain(m.output(0), e.input(0))
        workerManager.WorkerManager.RunSchedule(b.getSchedule())
        self.assertTrue(e.isFailed())
        self.assertFalse(e.isTerminated())

    def test_state(self):
        workerManager.WorkerManager.SetUseProcess(False)
        workerManager.WorkerManager.SetLogLevel(const.LogLevel.NoLog)
        b = box.Box("scene")
        m = MakeNumbers()
        e = RaiseError()
        b.addBlock(m)
        b.addBlock(e)
        e.param("value").set(5)
        chain.Chain(m.output(0), e.input(0))
        workerManager.WorkerManager.RunSchedule(b.getSchedule())
        self.assertEqual(workerManager.WorkerManager.ExecutionCount(), 5)
        self.assertTrue(workerManager.WorkerManager.TotalTime() > 0)
        self.assertEqual(workerManager.WorkerManager.AverageTime(), workerManager.WorkerManager.TotalTime() / float(workerManager.WorkerManager.ExecutionCount()))
        self.assertTrue(workerManager.WorkerManager.TimeLog(e.path()) > 0)
        self.assertTrue(workerManager.WorkerManager.TimeLog(m.path()) > 0)

        workerManager.WorkerManager.SetUseProcess(True)
        workerManager.WorkerManager.RunSchedule(b.getSchedule())
        self.assertEqual(workerManager.WorkerManager.ExecutionCount(), 5)
        self.assertTrue(workerManager.WorkerManager.TotalTime() > 0)
        self.assertEqual(workerManager.WorkerManager.AverageTime(), workerManager.WorkerManager.TotalTime() / float(workerManager.WorkerManager.ExecutionCount()))
        self.assertTrue(workerManager.WorkerManager.TimeLog(e.path()) > 0)
        self.assertTrue(workerManager.WorkerManager.TimeLog(m.path()) > 0)

    def test_logging(self):
        workerManager.WorkerManager.SetLogLevel(const.LogLevel.NoLog)
        workerManager.WorkerManager.SetUseProcess(True)
        b = box.Box("scene")
        m = MakeNumbers()
        e = RaiseError()
        e2 = RaiseError()
        b.addBlock(m)
        b.addBlock(e)
        b.addBlock(e2)
        e.param("value").set(5)
        chain.Chain(m.output(0), e.input(0))
        chain.Chain(m.output(0), e2.input(0))
        workerManager.WorkerManager.RunSchedule(b.getSchedule())

        self.assertEqual(len(workerManager.WorkerManager.ErrorLogs().keys()), 2)
        self.assertEqual(len(workerManager.WorkerManager.ErrorLog(e2.path())), 2)
        self.assertEqual(len(workerManager.WorkerManager.WarnLogs().keys()), 1)
        self.assertEqual(len(workerManager.WorkerManager.WarnLog(m.path())), 1)
        self.assertEqual(len(workerManager.WorkerManager.DebugLog(e.path())), 6)
        self.assertEqual(len(workerManager.WorkerManager.DebugLog(e2.path())), 1)

        workerManager.WorkerManager.SetUseProcess(False)
        workerManager.WorkerManager.RunSchedule(b.getSchedule())

        self.assertEqual(len(workerManager.WorkerManager.ErrorLogs().keys()), 2)
        self.assertEqual(len(workerManager.WorkerManager.ErrorLog(e2.path())), 2)
        self.assertEqual(len(workerManager.WorkerManager.WarnLogs().keys()), 1)
        self.assertEqual(len(workerManager.WorkerManager.WarnLog(m.path())), 1)
        self.assertEqual(len(workerManager.WorkerManager.DebugLog(e.path())), 6)
        self.assertEqual(len(workerManager.WorkerManager.DebugLog(e2.path())), 1)

        
if __name__ == "__main__":
    unittest.main()
