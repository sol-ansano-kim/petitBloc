import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import box
from petitBloc import block
from petitBloc import chain
from petitBloc import port
from petitBloc import manager
import multiprocessing


class DmpStr(block.Block):
    def __init__(self, name=""):
        super(DmpStr, self).__init__(name=name)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(str)

    def process(self):
        p = self.input(0).receive()
        if p.isEOP():
            return False

        self.dmp.put(p.value())
        p.drop()
        
        return True


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
        

if __name__ == "__main__":
    unittest.main()
