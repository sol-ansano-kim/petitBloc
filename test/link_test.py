import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import box
from petitBloc import block
from petitBloc import chain
from petitBloc import anytype
from petitBloc import workerManager
import Queue
import multiprocessing


class NumberGen(block.Block):
    def __init__(self):
        super(NumberGen, self).__init__()

    def initialize(self):
        self.addParam(int, "number")
        self.addParam(int, "count")
        self.addOutput(int, "output")

    def run(self):
        for i in range(self.param("count").get()):
            self.output("output").send(self.param("number").get())


class LinkParam(block.Block):
    def __init__(self):
        super(LinkParam, self).__init__()
        self.eop = multiprocessing.Value("i", 0)
        self.dmp = multiprocessing.Queue()

    def _getDumped(self):
        dumped = []
        while (not self.dmp.empty()):
            dumped.append(self.dmp.get())

        return dumped

    def initialize(self):
        in_p = self.addInput(int, "in1")
        self.addInput(int, "in2")
        param = self.addParam(int, "integer")
        in_p.linkParam(param)

    def run(self):
        self.eop.value = 0
        while (not self.dmp.empty()):
            self.dmp.get()
        super(LinkParam, self).run()

    def process(self):
        inp_1 = self.input("in1").receive()

        if inp_1.isEOP():
            self.eop.value = 1
            return False

        inp_2 = self.input("in2").receive()

        if inp_2.isEOP():
            return False

        v1 = inp_1.value()
        v2 = inp_2.value()

        inp_1.drop()
        inp_2.drop()
        self.dmp.put(v1 + v2)

        return True


class LinkTest(unittest.TestCase):
    def test_link(self):
        b = block.Block()
        param_str = b.addParam(str, "str")
        param_int = b.addParam(int, "int")
        param_float = b.addParam(float, "float")
        param_bool = b.addParam(bool, "bool")

        input_str = b.addInput(str, "str")
        input_int = b.addInput(int, "int")
        input_float = b.addInput(float, "float")
        input_bool = b.addInput(bool, "bool")
        input_any = b.addInput(anytype.AnyType, "any")

        self.assertTrue(input_str.linkParam(param_str))
        self.assertTrue(input_str.hasLinkedParam())
        input_str.unlinkParam()
        self.assertFalse(input_str.hasLinkedParam())
        self.assertFalse(input_str.linkParam(param_int))
        input_str.unlinkParam()
        self.assertFalse(input_str.linkParam(param_float))
        input_str.unlinkParam()
        self.assertFalse(input_str.linkParam(param_bool))
        input_str.unlinkParam()

        self.assertFalse(input_int.linkParam(param_str))
        input_int.unlinkParam()
        self.assertTrue(input_int.linkParam(param_int))
        self.assertTrue(input_int.hasLinkedParam())
        input_int.unlinkParam()
        self.assertFalse(input_int.hasLinkedParam())
        self.assertTrue(input_int.linkParam(param_float))
        input_int.unlinkParam()
        self.assertTrue(input_int.linkParam(param_bool))
        input_int.unlinkParam()

        self.assertFalse(input_float.linkParam(param_str))
        input_float.unlinkParam()
        self.assertTrue(input_float.linkParam(param_int))
        self.assertTrue(input_float.hasLinkedParam())
        input_float.unlinkParam()
        self.assertFalse(input_float.hasLinkedParam())
        self.assertTrue(input_float.linkParam(param_float))
        input_float.unlinkParam()
        self.assertTrue(input_float.linkParam(param_bool))
        input_float.unlinkParam()

        self.assertFalse(input_bool.linkParam(param_str))
        input_bool.unlinkParam()
        self.assertTrue(input_bool.linkParam(param_int))
        self.assertTrue(input_bool.hasLinkedParam())
        input_bool.unlinkParam()
        self.assertFalse(input_bool.hasLinkedParam())
        self.assertTrue(input_bool.linkParam(param_float))
        input_bool.unlinkParam()
        self.assertTrue(input_bool.linkParam(param_bool))
        input_bool.unlinkParam()

        self.assertTrue(input_any.linkParam(param_str))
        self.assertTrue(input_any.hasLinkedParam())
        input_any.unlinkParam()
        self.assertFalse(input_any.hasLinkedParam())
        self.assertTrue(input_any.linkParam(param_int))
        input_any.unlinkParam()
        self.assertTrue(input_any.linkParam(param_float))
        input_any.unlinkParam()
        self.assertTrue(input_any.linkParam(param_bool))
        input_any.unlinkParam()

    def test_receive(self):
        b = block.Block()
        param_int = b.addParam(int, "int")
        input_int = b.addInput(int, "int")
        p = input_int.receive()

        self.assertTrue(p.isEOP())

        self.assertTrue(input_int.linkParam(param_int))
        p = input_int.receive()
        self.assertFalse(p.isEOP())
        self.assertEqual(p.value(), 0)

        param_int.set(1)
        p = input_int.receive()
        self.assertFalse(p.isEOP())
        self.assertEqual(p.value(), 1)

        p = input_int.receive()
        self.assertFalse(p.isEOP())
        self.assertEqual(p.value(), 1)

        param_int.set(100)
        p = input_int.receive()
        self.assertFalse(p.isEOP())
        self.assertEqual(p.value(), 100)

    def test_link_process(self):
        g = box.Box()
        num1 = NumberGen()
        num2 = NumberGen()
        num1.param("number").set(10)
        num1.param("count").set(1)
        num2.param("number").set(1)
        num2.param("count").set(3)
        lp = LinkParam()
        self.assertTrue(g.addBlock(num1))
        self.assertTrue(g.addBlock(num2))
        self.assertTrue(g.addBlock(lp))

        c1 = chain.Chain(num1.output("output"), lp.input("in1"))
        c2 = chain.Chain(num2.output("output"), lp.input("in2"))
        self.assertIsNotNone(c1)
        self.assertIsNotNone(c2)

        schedule = g.getSchedule()

        workerManager.WorkerManager.RunSchedule(schedule)
        workerManager.WorkerManager.SetUseProcess(True)
        self.assertTrue(lp.eop.value)
        self.assertEqual(lp._getDumped(), [11])

        workerManager.WorkerManager.RunSchedule(schedule)
        self.assertTrue(lp.eop.value)
        self.assertEqual(lp._getDumped(), [11])

        c1.disconnect()

        lp.param("integer").set(10)
        workerManager.WorkerManager.RunSchedule(schedule)
        workerManager.WorkerManager.SetUseProcess(True)
        self.assertFalse(lp.eop.value)
        self.assertEqual(lp._getDumped(), [11, 11, 11])

        workerManager.WorkerManager.RunSchedule(schedule)
        self.assertFalse(lp.eop.value)
        self.assertEqual(lp._getDumped(), [11, 11, 11])


if __name__ == "__main__":
    unittest.main()
