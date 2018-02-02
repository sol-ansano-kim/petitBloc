import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import port
from petitBloc import chain
from petitBloc import block
from petitBloc import core
from petitBloc import parameter
from petitBloc import box
from petitBloc import const
from petitBloc import workerManager
import Queue
import multiprocessing


class DmpStr(block.Block):
    def __init__(self, name=""):
        super(DmpStr, self).__init__(name=name)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(str)
        self.addParam(str, "testStr")

    def process(self):
        self.dmp.put(self.param("testStr").get())

        return False


class DmpInt(block.Block):
    def __init__(self, name=""):
        super(DmpInt, self).__init__(name=name)
        self.dmp = multiprocessing.Queue()

    def initialize(self):
        self.addInput(int)
        self.addParam(int, "testInt")

    def process(self):
        self.dmp.put(self.param("testInt").get())

        return False


class DumpParam(block.Block):
    def __init__(self, name="", parent=None):
        super(DumpParam, self).__init__(name=name, parent=parent)
        self.dmp = Queue.Queue()
        self.__process = False

    def initialize(self):
        self.addParam(str, "str1")
        self.addParam(str, "str2")
        self.addParam(float, "float1")
        self.addParam(float, "float2")

    def useProcess(self, v):
        self.__process = v
        self.flush()

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
        self.dmp.put(self.param("str1").get())
        self.dmp.put(self.param("float1").get())

        return False


class TestParameter(unittest.TestCase):
    def test_init(self):
        p1 = parameter.Parameter("testStr", value="test")
        self.assertIsNotNone(p1)
        self.assertEqual(p1.typeClass(), str)
        self.assertEqual(str(p1), "Parameter<'testStr'>")
        p2 = parameter.Parameter("testInt", value=1)
        self.assertIsNotNone(p2)
        self.assertEqual(p2.typeClass(), int)
        p3 = parameter.Parameter("testInt", value=1.0)
        self.assertIsNotNone(p3)
        self.assertEqual(p3.typeClass(), float)
        p4 = parameter.Parameter("testBool", value=True)
        self.assertIsNotNone(p4)
        self.assertEqual(p4.typeClass(), bool)

        p5 = parameter.Parameter("castFloat", typeClass=float, value=False)
        self.assertIsNotNone(p5)
        self.assertEqual(p5.typeClass(), float)
        self.assertEqual(p5.get(), 0.0)

        p6 = parameter.Parameter("castBool", typeClass=bool, value=0)
        self.assertIsNotNone(p6)
        self.assertEqual(p6.typeClass(), bool)
        self.assertEqual(p6.get(), False)

        p7 = parameter.Parameter("castStr", typeClass=str, value=0)
        self.assertIsNone(p7)

        p8 = parameter.Parameter("castInt", typeClass=int, value="Asd")
        self.assertIsNone(p8)

        p9 = parameter.Parameter("typeInt", typeClass=int)
        self.assertIsNotNone(p9)

    def test_get_set(self):
        p1 = parameter.Parameter("testStr", str)
        self.assertEqual(p1.get(), "")
        self.assertTrue(p1.set(u"a"))
        self.assertEqual(p1.get(), "a")
        self.assertFalse(p1.set(1))
        p2 = parameter.Parameter("testInt", typeClass=int, value=0)
        self.assertTrue(p2.set(1.12312))
        self.assertTrue(isinstance(p2.get(), int))
        self.assertEqual(p2.get(), 1)


class TestEnum(unittest.TestCase):
    def test_init(self):
        self.assertIsNone(parameter.EnumParameter("test", []))
        self.assertIsNone(parameter.EnumParameter("test", "a"))
        self.assertIsNone(parameter.EnumParameter("test", 1))
        self.assertIsNotNone(parameter.EnumParameter("test", ["a", "b", "c"]))
        self.assertIsNotNone(parameter.EnumParameter("test", ["a", "b", "c"], value=0))

    def test_test(self):
        p1 = parameter.EnumParameter("test", ["a", "b", "c"])
        self.assertEqual(p1.get(), 0)
        self.assertEqual(p1.getLabel(), "a")
        self.assertEqual(p1.getLabels(), ["a", "b", "c"])
        self.assertTrue(p1.set(1))
        self.assertEqual(p1.getLabel(), "b")
        self.assertFalse(p1.set(4))
        self.assertEqual(p1.getLabel(), "b")

        p2 = parameter.EnumParameter("test", ["a", "b", "c"], value=2)
        self.assertEqual(p2.get(), 2)
        self.assertEqual(p2.getLabel(), "c")

        p3 = parameter.EnumParameter("test", ["a", "b", "c"], value=5)
        self.assertEqual(p3.get(), 0)

        p4 = parameter.EnumParameter("test", ["a", "b", "c"], value=-1)
        self.assertEqual(p4.get(), 0)


class TestBlock(unittest.TestCase):
    def test_init(self):
        b = block.Block()
        self.assertIsNotNone(b)

        p = b.addParam()
        self.assertIsNone(p)

        p = b.addParam(str)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param")
        self.assertEqual(p.get(), "")

        p = b.addParam(int)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param1")
        self.assertEqual(p.get(), 0)

        p = b.addParam(float)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param2")
        self.assertEqual(p.get(), 0.0)

        p = b.addParam(bool)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "param3")
        self.assertEqual(p.get(), False)

        p = b.addParam(list)
        self.assertIsNone(p)

        p = b.addParam(name="intNumber", value=1)
        self.assertIsNotNone(p)
        self.assertEqual(p.name(), "intNumber")
        self.assertEqual(p.typeClass(), int)
        self.assertEqual(p.get(), 1)

    def test_run(self):
        dmp_str = DmpStr()
        dmp_int = DmpInt()

        self.assertTrue(dmp_str.param("testStr").set("HELLO"))
        self.assertTrue(dmp_int.param("testInt").set(23))
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

    def test_run(self):
        box1 = box.Box()
        dmp_str = DmpStr()
        dmp_int = DmpInt()
        self.assertTrue(box1.addBlock(dmp_str))
        self.assertTrue(box1.addBlock(dmp_int))

        dmp_str.param("testStr").set("HELLO")
        dmp_int.param("testInt").set(23)

        schedule = box1.getSchedule()
        workerManager.WorkerManager.RunSchedule(schedule)

        str_val = []
        while (not dmp_str.dmp.empty()):
            str_val.append(dmp_str.dmp.get())

        self.assertEqual(str_val, ["HELLO"])

        int_val = []
        while (not dmp_int.dmp.empty()):
            int_val.append(dmp_int.dmp.get())

        self.assertEqual(int_val, [23])

    def test_expression_path(self):
        box1 = box.Box("main")
        box2 = box.Box("subn")

        box1.addParam(str, "v1")
        box2.addParam(str, "v1")
        box1.addParam(float, "v2")
        box2.addParam(float, "v2")
        box1.param("v1").set("HELLO")
        box2.param("v1").set("WORLD")
        box1.param("v2").set(2.5)
        box2.param("v2").set(3.5)

        param_bloc = DumpParam()
        param_bloc.useProcess(False)
        box2.addBlock(param_bloc)
        box1.addBlock(box2)

        param_bloc.param("str1").set("no expr")
        param_bloc.param("str2").set("Hello")
        self.assertFalse(param_bloc.param("str1").hasExpression())
        self.assertFalse(param_bloc.param("str1").setExpression("1 * 2"))
        self.assertTrue(param_bloc.param("str1").setExpression("= 1 * 2"))
        self.assertTrue(param_bloc.param("str1").hasExpression())
        self.assertFalse(param_bloc.param("str1").validExpression())
        self.assertTrue(param_bloc.param("str1").setExpression("= 'asda'.upper()"))
        self.assertTrue(param_bloc.param("str1").hasExpression())
        self.assertEqual(param_bloc.param("str1").get(), "ASDA")
        self.assertTrue(param_bloc.param("str1").validExpression())
        self.assertTrue(param_bloc.param("str1").setExpression("= './@str2'"))
        self.assertEqual(param_bloc.param("str1").getExpression(), "= './@str2'")
        self.assertEqual(param_bloc.param("str1").get(), param_bloc.param("str2").get())
        self.assertTrue(param_bloc.param("str1").setExpression("= '../@v1'"))
        self.assertEqual(param_bloc.param("str1").getExpression(), "= '../@v1'")
        self.assertEqual(param_bloc.param("str1").get(), box2.param("v1").get())
        self.assertTrue(param_bloc.param("str1").setExpression(None))
        self.assertFalse(param_bloc.param("str1").hasExpression())
        self.assertEqual(param_bloc.param("str1").get(), "no expr")
        self.assertTrue(param_bloc.param("str1").setExpression("= '{} {}'.format('/main@v1', '/main/subn@v1')"))
        self.assertEqual(param_bloc.param("str1").getExpression(), "= '{} {}'.format('/main@v1', '/main/subn@v1')")
        self.assertEqual(param_bloc.param("str1").get(), "{} {}".format(box1.param("v1").get(), box2.param("v1").get()))
        self.assertTrue(param_bloc.param("str1").hasExpression())

        param_bloc.param("float1").set(1.1)
        param_bloc.param("float2").set(2.2)
        self.assertFalse(param_bloc.param("float1").hasExpression())
        self.assertFalse(param_bloc.param("float1").setExpression("1 * 2"))
        self.assertTrue(param_bloc.param("float1").setExpression("= 1 * 2"))
        self.assertEqual(param_bloc.param("float1").get(), 2.0)
        self.assertTrue(param_bloc.param("float1").setExpression("= ./@float2"))
        self.assertEqual(param_bloc.param("float1").get(), param_bloc.param("float2").get())
        self.assertEqual(param_bloc.param("float1").get(), param_bloc.param("float2").get())
        self.assertTrue(param_bloc.param("float1").setExpression(None))
        self.assertFalse(param_bloc.param("float1").hasExpression())
        self.assertEqual(param_bloc.param("float1").get(), 1.1)
        self.assertTrue(param_bloc.param("float1").setExpression("= ../@v2"))
        self.assertEqual(param_bloc.param("float1").get(), box2.param("v2").get())
        self.assertTrue(param_bloc.param("float1").setExpression("= ../@v2 * ../../@v2"))
        self.assertEqual(param_bloc.param("float1").get(), box2.param("v2").get() * box1.param("v2").get())
        self.assertTrue(param_bloc.param("float1").hasExpression())

        param_bloc.flush()
        workerManager.WorkerManager.RunSchedule(box1.getSchedule())

        res = []
        while (not param_bloc.dmp.empty()):
            res.append(param_bloc.dmp.get())

        self.assertEqual(res, ["{} {}".format(box1.param("v1").get(), box2.param("v1").get()), box1.param("v2").get() * box2.param("v2").get()])

        workerManager.WorkerManager.SetUseProcess(True)
        param_bloc.useProcess(True)
        param_bloc.flush()
        workerManager.WorkerManager.RunSchedule(box1.getSchedule())

        res = []
        while (not param_bloc.dmp.empty()):
            res.append(param_bloc.dmp.get())

        self.assertEqual(res, ["{} {}".format(box1.param("v1").get(), box2.param("v1").get()), box1.param("v2").get() * box2.param("v2").get()])

    def test_context(self):
        box1 = box.Box("main")
        box2 = box.Box("subn")
        box1.addBlock(box2)
        box1.addParam(str, "str")
        box2.addParam(int, "int")
        box1.param("str").set("WORLD")
        box2.param("int").set(20)
        dump = DumpParam()

        box2.addBlock(dump)

        self.assertIsNotNone(box1.createContext())
        self.assertIsNone(box1.createContext())
        self.assertIsNone(box2.createContext())
        self.assertEqual(box1.getContext(), {})

        self.assertIsNotNone(box1.addContext(str, "contextStr"))
        self.assertIsNotNone(box1.addContext(int, "contextInt"))
        self.assertIsNone(box2.addContext(str, "contextStr"))
        self.assertIsNone(box2.addContext(int, "contextInt"))
        self.assertEqual(box1.getContext(), {"contextStr": "", "contextInt": 0})

        self.assertIsNotNone(box1.context("contextStr"))
        self.assertIsNotNone(box1.context("contextInt"))
        self.assertIsNone(box2.context("contextStr"))
        self.assertIsNone(box2.context("contextInt"))

        for p in box2.contexts():
            self.assertTrue(False)

        c1 = box1.context("contextStr")
        self.assertTrue(box1.removeContext(c1))
        self.assertFalse(box1.removeContext("contextStr"))
        c2 = box1.context("contextInt")
        self.assertTrue(box1.removeContext("contextInt"))
        self.assertFalse(box1.removeContext(c2))

        self.assertIsNotNone(box1.addContext(str, "contextStr"))
        self.assertIsNotNone(box1.addContext(int, "contextInt"))
        self.assertEqual(box1.getContext(), {"contextStr": "", "contextInt": 0})
        c1 = box1.context("contextStr")
        c2 = box1.context("contextInt")
        c1.set("HELLO")
        c2.set(5)
        self.assertEqual(box1.getContext(), {"contextStr": "HELLO", "contextInt": 5})

        self.assertTrue(dump.param("str1").setExpression("= '$contextStr'"))
        self.assertTrue(dump.param("str1").setExpression("= '$contextStr'.lower()"))
        self.assertEqual(dump.param("str1").get(), "hello")
        self.assertTrue(dump.param("float1").setExpression("= $contextInt * 2"))
        self.assertEqual(dump.param("float1").get(), 10.0)

        self.assertTrue(dump.param("str1").setExpression("= '$contextStr' + ' ../../@str'"))
        self.assertTrue(dump.param("float1").setExpression("= $contextInt * ../@int"))

        self.assertEqual(dump.param("str1").get(), "HELLO WORLD")
        self.assertEqual(dump.param("float1").get(), 100.0)

        workerManager.WorkerManager.RunSchedule(box1.getSchedule())

        res = []
        while (not dump.dmp.empty()):
            res.append(dump.dmp.get())

        self.assertEqual(res, ["HELLO WORLD", 100.0])

        os.environ["TEST_ENV_STR"] = "!!!"
        os.environ["TEST_ENV_FLT"] = "0.5"

        self.assertTrue(dump.param("str1").setExpression("= '$contextStr' + ' ../../@str' + '$TEST_ENV_STR'"))
        self.assertTrue(dump.param("float1").setExpression("= $contextInt * ../@int * $TEST_ENV_FLT"))

        dump.flush()
        workerManager.WorkerManager.RunSchedule(box1.getSchedule())

        res = []
        while (not dump.dmp.empty()):
            res.append(dump.dmp.get())

        self.assertEqual(res, ["HELLO WORLD!!!", 50.0])


if __name__ == "__main__":
    unittest.main()
