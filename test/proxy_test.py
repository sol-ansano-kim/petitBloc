import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import box
from petitBloc import block
from petitBloc import chain
from petitBloc import port
from petitBloc import processManager
import multiprocessing


class MakeNumber(block.Block):
    def ___init__(self, name=""):
        super(MakeNumber, self).__init__(name=name)

    def initialize(self):
        self.addOutput(float)

    def process(self):
        for i in range(100):
            self.output(0).send(i)

        return False


class Double(block.Block):
    def __init__(self, name=""):
        super(Double, self).__init__(name=name)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)

    def process(self):
        p = self.input(0).receive()
        if p.isEOP():
            return False

        self.output(0).send(p.value() * 2)
        return True


class Add(block.Block):
    def __init__(self, name=""):
        super(Add, self).__init__(name=name)

    def initialize(self):
        self.addInput(float)
        self.addOutput(float)

    def process(self):
        p = self.input(0).receive()
        if p.isEOP():
            return False

        self.output(0).send(p.value() + 1)
        return True


class DmpFloat(block.Block):
    def __init__(self, name=""):
        super(DmpFloat, self).__init__(name=name)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(float)

    def flush(self):
        self.dmp.close()
        del self.dmp
        self.dmp = multiprocessing.Queue()

    def process(self):
        p = self.input(0).receive()
        if p.isEOP():
            return False

        self.dmp.put(p.value())
        return True


class ProxyParamTest(unittest.TestCase):
    def test_init(self):
        box1 = box.Box()
        param_bloc = block.ParamBlock("test")
        box1.addBlock(param_bloc)
        p = param_bloc.addParam(str, "testStr")

        self.assertIsNotNone(box1.addProxyParam(p))
        self.assertIsNone(box1.addProxyParam(p))
        p1 = box1.proxyParam("testStr")
        p2 = box1.proxyParam(0)
        self.assertEqual(p1, p2)
        self.assertEqual(p1.get(), "")
        self.assertTrue(p1.set("HELLO"))
        self.assertFalse(p1.set(0))
        self.assertEqual(p1.get(), "HELLO")

        self.assertTrue(box1.removeProxyParam(p1))
        self.assertFalse(box1.removeProxyParam(p2))


class ProxyPortTest(unittest.TestCase):
    def test_init(self):
        box1 = box.Box()
        self.assertTrue(box1.addInputProxy(int, "intProxy"))
        self.assertTrue(box1.hasInputProxy("intProxy"))
        self.assertTrue(box1.addInputProxy(bool, "boolProxy"))
        self.assertTrue(box1.hasInputProxy("boolProxy"))
        self.assertTrue(box1.addOutputProxy(int, "intProxy"))
        self.assertTrue(box1.hasOutputProxy("intProxy"))
        self.assertTrue(box1.addOutputProxy(bool, "boolProxy"))
        self.assertTrue(box1.hasOutputProxy("boolProxy"))
        self.assertEqual(len(box1.inputProxies()), 2)
        self.assertEqual(len(box1.outputProxies()), 2)

    def test_connect(self):
        box1 = box.Box("bigBox")
        box2 = box.Box("smallBox")
        self.assertTrue(box2.addInputProxy(float, "inFloat"))
        self.assertTrue(box2.hasInputProxy("inFloat"))
        self.assertTrue(box2.addOutputProxy(float, "outFloat"))
        self.assertTrue(box2.hasOutputProxy("outFloat"))
        num = MakeNumber()
        double = Double()
        dmp = DmpFloat()
        add = Add()

        box2.addBlock(double)
        box1.addBlock(num)
        box1.addBlock(dmp)
        box1.addBlock(box2)
        box1.addBlock(add)

        box1.connect(add.output(0), dmp.input(0))

        self.assertTrue(box2.connectInputProxy("inFloat", double.input(0)))
        self.assertFalse(box2.connectInputProxy("inFloat", double.output(0)))
        self.assertTrue(box2.connectOutputProxy("outFloat", double.output(0)))
        self.assertTrue(box2.connectOutputProxy("outFloat", dmp.input(0)))
        self.assertFalse(add.output(0).isConnected())
        self.assertTrue(box2.connectInputProxy("inFloat", add.output(0)))
        self.assertTrue(box2.connectOutputProxy("outFloat", add.input(0)))

        self.assertTrue(double.input(0).isConnected())
        self.assertTrue(double.output(0).isConnected())
        self.assertTrue(dmp.input(0).isConnected())
        self.assertTrue(add.input(0).isConnected())
        self.assertTrue(add.output(0).isConnected())
        self.assertIsNotNone(box2.inputProxy("inFloat"))
        self.assertIsNotNone(box2.outputProxy("outFloat"))

    def test_chain(self):
        box1 = box.Box("bigBox")
        box2 = box.Box("smallBox")
        num1 = MakeNumber()
        num2 = MakeNumber()
        doub1 = Double()
        doub2 = Double()
        add1 = Add()
        add2 = Add()

        box1.addBlock(box2)
        box1.addBlock(num1)
        box1.addBlock(num2)
        box2.addBlock(doub1)
        box2.addBlock(doub2)
        box1.addBlock(add1)
        box1.addBlock(add2)

        box2.addInputProxy(float, "in")
        box2.addOutputProxy(float, "out")

        self.assertTrue(box2.connectInputProxy("in", num1.output(0)))
        self.assertTrue(num1.output(0).isConnected())
        self.assertTrue(box2.connectInputProxy("in", num2.output(0)))
        self.assertEqual(box1.chainCount(), 1)
        self.assertFalse(num1.output(0).isConnected())
        self.assertTrue(num2.output(0).isConnected())

        self.assertTrue(box2.connectInputProxy("in", doub1.input(0)))
        self.assertTrue(doub1.input(0).isConnected())
        self.assertTrue(box2.connectInputProxy("in", doub2.input(0)))
        self.assertEqual(box2.chainCount(), 2)
        self.assertTrue(doub1.input(0).isConnected())
        self.assertTrue(doub2.input(0).isConnected())
        self.assertTrue(box2.connectOutputProxy("out", doub1.output(0)))
        self.assertTrue(doub1.output(0).isConnected())
        self.assertEqual(box2.chainCount(), 3)
        self.assertTrue(box2.connectOutputProxy("out", doub2.output(0)))
        self.assertEqual(box2.chainCount(), 3)
        self.assertFalse(doub1.output(0).isConnected())
        self.assertTrue(doub2.output(0).isConnected())

        self.assertTrue(box2.connectOutputProxy("out", add1.input(0)))
        self.assertEqual(box2.chainCount(), 3)
        self.assertEqual(box1.chainCount(), 2)
        self.assertTrue(add1.input(0).isConnected())
        self.assertTrue(box2.connectOutputProxy("out", add2.input(0)))
        self.assertEqual(box2.chainCount(), 3)
        self.assertEqual(box1.chainCount(), 3)
        self.assertTrue(add1.input(0).isConnected())
        self.assertTrue(add2.input(0).isConnected())

        self.assertTrue(box2.addInputProxy(float, "in2"))
        self.assertTrue(box2.connectInputProxy("in2", doub2.input(0)))
        self.assertEqual(box2.chainCount(), 3)
        self.assertTrue(box2.connectInputProxy("in2", doub1.input(0)))
        self.assertEqual(box2.chainCount(), 3)

    def test_run(self):
        box1 = box.Box("bigBox")
        box2 = box.Box("smallBox")
        num = MakeNumber()
        double = Double()
        dmp = DmpFloat()
        add = Add()
        box1.addBlock(num)
        box1.addBlock(dmp)
        box1.addBlock(box2)
        box1.addBlock(add)
        box2.addBlock(double)

        box2.addInputProxy(float, "inFloat")
        box2.addOutputProxy(float, "outFloat")

        self.assertTrue(box2.connectInputProxy("inFloat", num.output(0)))
        self.assertTrue(box2.connectInputProxy("inFloat", double.input(0)))
        self.assertTrue(box2.connectOutputProxy("outFloat", double.output(0)))
        self.assertTrue(box2.connectOutputProxy("outFloat", add.input(0)))
        self.assertTrue(box1.connect(add.output(0), dmp.input(0)))

        processManager.RunSchedule(box1.getSchedule())

        vals = []
        for i in range(100):
            vals.append(float(i * 2) + 1)

        dmped = []
        while (not dmp.dmp.empty()):
            dmped.append(dmp.dmp.get())

        self.assertEqual(vals, dmped)

    def test_box_to_box(self):
        box1 = box.Box("bigBox")
        box2 = box.Box("mulBox")
        box3 = box.Box("addBox")

        num = MakeNumber()
        double = Double()
        dmp = DmpFloat()
        add = Add()

        box1.addBlock(num)
        box1.addBlock(dmp)
        box1.addBlock(box2)
        box1.addBlock(box3)
        box2.addBlock(double)
        box3.addBlock(add)

        box2.addInputProxy(float, "inFloat")
        box2.addOutputProxy(float, "outFloat")
        box3.addInputProxy(float, "inFloat")
        box3.addOutputProxy(float, "outFloat")

        self.assertTrue(box2.connectInputProxy("inFloat", num.output(0)))
        self.assertTrue(box2.connectInputProxy("inFloat", double.input(0)))
        self.assertTrue(box2.connectOutputProxy("outFloat", double.output(0)))

        self.assertTrue(box3.connectInputProxy("inFloat", box2.outputProxy("outFloat")))
        self.assertTrue(box3.connectInputProxy("inFloat", add.input(0)))
        self.assertTrue(box3.connectOutputProxy("outFloat", add.output(0)))
        self.assertTrue(box3.connectOutputProxy("outFloat", dmp.input(0)))

        processManager.RunSchedule(box1.getSchedule())

        vals = []
        for i in range(100):
            vals.append(float(i * 2) + 1)

        dmped = []
        while (not dmp.dmp.empty()):
            dmped.append(dmp.dmp.get())

        self.assertEqual(vals, dmped)


if __name__ == "__main__":
    unittest.main()
