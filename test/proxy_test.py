import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import box
from petitBloc import block
from petitBloc import chain
from petitBloc import port
from petitBloc import workerManager
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
        bloc = block.Block()
        box1.addBlock(bloc)
        p = bloc.addParam(str, "testStr")

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
        ip, op = box1.addInputProxy(int, "intProxy")
        self.assertIsNotNone(ip)
        self.assertIsNotNone(op)
        self.assertTrue(box1.hasInputProxy("intProxy"))
        ip, op = box1.addInputProxy(bool, "boolProxy")
        self.assertIsNotNone(ip)
        self.assertIsNotNone(op)
        self.assertTrue(box1.hasInputProxy("boolProxy"))
        ip, op = box1.addOutputProxy(int, "intProxy")
        self.assertIsNotNone(ip)
        self.assertIsNotNone(op)
        self.assertTrue(box1.hasOutputProxy("intProxy"))
        op, op = box1.addOutputProxy(bool, "boolProxy")
        self.assertIsNotNone(ip)
        self.assertIsNotNone(op)
        self.assertTrue(box1.hasOutputProxy("boolProxy"))
        self.assertEqual(len(box1.inputProxies()), 2)
        self.assertEqual(len(box1.outputProxies()), 2)

    def test_connect(self):
        box1 = box.Box("bigBox")
        box2 = box.Box("smallBox")
        ip, op = box2.addInputProxy(float, "inFloat")
        self.assertIsNotNone(ip)
        self.assertIsNotNone(op)
        self.assertTrue(box2.hasInputProxy("inFloat"))
        ip, op = box2.addOutputProxy(float, "outFloat")
        self.assertIsNotNone(ip)
        self.assertIsNotNone(op)
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

        chain.Chain(add.output(0), dmp.input(0))

        self.assertIsNotNone(chain.Chain(box2.inputProxyOut("inFloat"), double.input(0)))
        self.assertIsNotNone(chain.Chain(double.output(0), box2.outputProxyIn("outFloat")))
        self.assertIsNotNone(chain.Chain(box2.outputProxyOut("outFloat"), dmp.input(0)))
        self.assertFalse(add.output(0).isConnected())
        self.assertIsNotNone(chain.Chain(add.output(0), box2.inputProxyIn("inFloat")))
        self.assertIsNotNone(chain.Chain(box2.outputProxyOut("outFloat"), add.input(0)))

        self.assertTrue(double.input(0).isConnected())
        self.assertTrue(double.output(0).isConnected())
        self.assertTrue(dmp.input(0).isConnected())
        self.assertTrue(add.input(0).isConnected())
        self.assertTrue(add.output(0).isConnected())
        self.assertIsNotNone(box2.inputProxyIn("inFloat"))
        self.assertIsNotNone(box2.outputProxyOut("outFloat"))

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

        self.assertIsNotNone(chain.Chain(num1.output(0), box2.inputProxyIn("in")))
        self.assertTrue(num1.output(0).isConnected())
        self.assertIsNotNone(chain.Chain(num2.output(0), box2.inputProxyIn("in")))
        self.assertFalse(num1.output(0).isConnected())
        self.assertTrue(num2.output(0).isConnected())

        self.assertIsNotNone(chain.Chain(box2.inputProxyOut("in"), doub1.input(0)))
        self.assertTrue(doub1.input(0).isConnected())
        self.assertIsNotNone(chain.Chain(box2.inputProxyOut("in"), doub2.input(0)))
        self.assertTrue(doub1.input(0).isConnected())
        self.assertTrue(doub2.input(0).isConnected())
        self.assertIsNotNone(chain.Chain(doub1.output(0), box2.outputProxyIn("out")))
        self.assertTrue(doub1.output(0).isConnected())
        self.assertIsNotNone(chain.Chain(doub2.output(0), box2.outputProxyIn("out")))
        self.assertFalse(doub1.output(0).isConnected())
        self.assertTrue(doub2.output(0).isConnected())

        self.assertIsNotNone(chain.Chain(box2.outputProxyOut("out"), add1.input(0)))
        self.assertTrue(add1.input(0).isConnected())
        self.assertIsNotNone((chain.Chain(box2.outputProxyOut("out"), add2.input(0))))
        self.assertTrue(add1.input(0).isConnected())
        self.assertTrue(add2.input(0).isConnected())

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

        self.assertIsNotNone(chain.Chain(num.output(0), box2.inputProxyIn("inFloat")))
        self.assertIsNotNone(chain.Chain(box2.inputProxyOut("inFloat"), double.input(0)))
        self.assertIsNotNone(chain.Chain(double.output(0), box2.outputProxyIn("outFloat")))
        self.assertIsNotNone(chain.Chain(box2.outputProxyOut("outFloat"), add.input(0)))
        self.assertIsNotNone(chain.Chain(add.output(0), dmp.input(0)))

        workerManager.WorkerManager.RunSchedule(box1.getSchedule())

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

        chain.Chain(num.output(0), box2.inputProxyIn("inFloat"))
        chain.Chain(box2.inputProxyOut("inFloat"), double.input(0))
        chain.Chain(double.output(0), box2.outputProxyIn("outFloat"))
        chain.Chain(box2.outputProxyOut("outFloat"), box3.inputProxyIn("inFloat"))
        chain.Chain(box3.inputProxyOut("inFloat"), add.input(0))
        chain.Chain(add.output(0), box3.outputProxyIn("outFloat"))
        chain.Chain(box3.outputProxyOut("outFloat"), dmp.input(0))

        workerManager.WorkerManager.RunSchedule(box1.getSchedule())

        vals = []
        for i in range(100):
            vals.append(float(i * 2) + 1)

        dmped = []
        while (not dmp.dmp.empty()):
            dmped.append(dmp.dmp.get())

        self.assertEqual(vals, dmped)


if __name__ == "__main__":
    unittest.main()
