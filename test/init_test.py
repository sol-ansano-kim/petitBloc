import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import port
from petitBloc import chain
from petitBloc import block
from petitBloc import core
from petitBloc import box
from petitBloc import manager
import multiprocessing


class DmpStr(block.Block):
    def __init__(self, name=""):
        super(DmpStr, self).__init__(name=name)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(str)

    def process(self):
        p = self.input().receive()
        if p.isEOP():
            return False

        self.dmp.put(p.value())

        return True


class DmpInt(block.Block):
    def __init__(self, name=""):
        super(DmpInt, self).__init__(name=name)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(int)

    def process(self):
        p = self.input().receive()
        if p.isEOP():
            return False

        self.dmp.put(p.value())

        return True


class TestParameter(unittest.TestCase):
    def test_init(self):
        p1 = core.Parameter("testStr", value="test")
        self.assertIsNotNone(p1)
        self.assertEqual(p1.typeClass(), str)
        self.assertEqual(str(p1), "Parameter<'testStr'>")
        p2 = core.Parameter("testInt", value=1)
        self.assertIsNotNone(p2)
        self.assertEqual(p2.typeClass(), int)
        p3 = core.Parameter("testInt", value=1.0)
        self.assertIsNotNone(p3)
        self.assertEqual(p3.typeClass(), float)
        p4 = core.Parameter("testBool", value=True)
        self.assertIsNotNone(p4)
        self.assertEqual(p4.typeClass(), bool)

        p5 = core.Parameter("castFloat", typeClass=float, value=False)
        self.assertIsNotNone(p5)
        self.assertEqual(p5.typeClass(), float)
        self.assertEqual(p5.get(), 0.0)

        p6 = core.Parameter("castBool", typeClass=bool, value=0)
        self.assertIsNotNone(p6)
        self.assertEqual(p6.typeClass(), bool)
        self.assertEqual(p6.get(), False)

        p7 = core.Parameter("castStr", typeClass=str, value=0)
        self.assertIsNone(p7)

        p8 = core.Parameter("castInt", typeClass=int, value="Asd")
        self.assertIsNone(p8)

        p9 = core.Parameter("typeInt", typeClass=int)
        self.assertIsNotNone(p9)

    def test_get_set(self):
        p1 = core.Parameter("testStr", str)
        self.assertEqual(p1.get(), "")
        self.assertTrue(p1.set(u"a"))
        self.assertEqual(p1.get(), "a")
        self.assertFalse(p1.set(1))
        p2 = core.Parameter("testInt", 0, int)


class TestInitBlock(unittest.TestCase):
    def test_init(self):
        b = block.ParamBlock(name="Param")
        self.assertIsNotNone(b)

        p = b.addParam()
        self.assertIsNone(p)

        p = b.addParam(str)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param")
        self.assertEqual(p.get(), "")
        self.assertIsNotNone(b.outputFromName(p.name()))

        p = b.addParam(int)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param1")
        self.assertEqual(p.get(), 0)
        self.assertIsNotNone(b.outputFromName(p.name()))

        p = b.addParam(float)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param2")
        self.assertEqual(p.get(), 0.0)
        self.assertIsNotNone(b.outputFromName(p.name()))

        p = b.addParam(bool)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param3")
        self.assertEqual(p.get(), False)
        self.assertIsNotNone(b.outputFromName(p.name()))

        p = b.addParam(list)
        self.assertIsNone(p)

        p = b.addParam(name="intNumber", value=1)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "intNumber")
        self.assertEqual(p.typeClass(), int)
        self.assertEqual(p.get(), 1)
        self.assertIsNotNone(b.outputFromName(p.name()))

        count = 0
        for p in b.params():
            count += 1

        self.assertEqual(count, 5)

        count = 0
        for p in b.outputs():
            count += 1

        self.assertEqual(count, 5)

        count = 0
        for p in b.inputs():
            count += 1

        self.assertEqual(count, 0)

        self.assertIsNone(b.addInput(str))
        self.assertIsNone(b.addOutput(str))

    def test_run(self):
        b = block.ParamBlock("test")
        b.addParam(str, "testStr")
        b.addParam(int, "testInt")

        p1 = b.outputFromName("testStr")
        self.assertIsNotNone(p1)
        p2 = b.outputFromName("testInt")
        self.assertIsNotNone(p2)

        dmp_str = DmpStr()
        dmp_int = DmpInt()

        self.assertIsNotNone(chain.Chain(p1, dmp_str.input()))
        self.assertIsNotNone(chain.Chain(p2, dmp_int.input()))

        self.assertTrue(b.paramFromName("testStr").set("HELLO"))
        self.assertTrue(b.paramFromName("testInt").set(23))
        b.activate()
        b.run()
        b.terminate()

        dmp_str.activate()
        dmp_str.run()

        dmp_int.activate()
        dmp_int.run()
        
        dmp_str.terminate()
        dmp_int.terminate()

        str_val = []
        while (not dmp_str.dmp.empty()):
            str_val.append(dmp_str.dmp.get())

        self.assertEqual(str_val, ["HELLO"])

        int_val = []
        while (not dmp_int.dmp.empty()):
            int_val.append(dmp_int.dmp.get())

        self.assertEqual(int_val, [23])

    def test_box(self):
        box1 = box.Box()

        pb = block.ParamBlock("test")
        dmp_str = DmpStr()
        dmp_int = DmpInt()
        self.assertTrue(box1.addBlock(pb))
        self.assertTrue(box1.addBlock(dmp_str))
        self.assertTrue(box1.addBlock(dmp_int))

        pb.addParam(str, "string")
        pb.addParam(int, "int")

        self.assertTrue(box1.connect(pb.outputFromName("string"), dmp_str.input()))
        self.assertTrue(box1.connect(pb.outputFromName("int"), dmp_int.input()))

        pb.paramFromName("string").set("HELLO")
        pb.paramFromName("int").set(23)

        schedule = box1.getSchedule()
        manager.RunSchedule(schedule)

        str_val = []
        while (not dmp_str.dmp.empty()):
            str_val.append(dmp_str.dmp.get())

        self.assertEqual(str_val, ["HELLO"])

        int_val = []
        while (not dmp_int.dmp.empty()):
            int_val.append(dmp_int.dmp.get())

        self.assertEqual(int_val, [23])


if __name__ == "__main__":
    unittest.main()
