import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from unitBlock import port
from unitBlock import packet
from unitBlock import chain


class PortTest(unittest.TestCase):
    def test_init(self):
        in_port1 = port.Port(str, port.Port.In)
        out_port1 = port.Port(str, port.Port.Out)
        in_port2 = port.InPort(str)
        out_port2 = port.OutPort(str)
        self.assertIsNotNone(in_port1)
        self.assertIsNotNone(out_port1)
        self.assertIsNotNone(in_port2)
        self.assertIsNotNone(out_port2)

    def test_send(self):
        in_port = port.InPort(str)
        out_port = port.OutPort(str)
        self.assertFalse(in_port.send("a"))
        self.assertFalse(out_port.send("b"))

    def test_receive(self):
        in_port = port.InPort(str)
        out_port = port.OutPort(str)
        self.assertIsNone(in_port.receive())
        self.assertIsNone(out_port.receive())

    def test_direction(self):
        in_port = port.InPort(str)
        out_port = port.OutPort(str)


class ChainTest(unittest.TestCase):
    def test_init(self):
        src_port1 = port.OutPort(str)
        dst_port1 = port.InPort(str)
        self.assertIsNotNone(chain.Chain(src_port1, dst_port1))
        self.assertIsNone(chain.Chain(dst_port1, src_port1))
        self.assertIsNone(chain.Chain(dst_port1, dst_port1))
        self.assertIsNone(chain.Chain(src_port1, src_port1))

        src_port2 = port.OutPort(int)
        src_port3 = port.OutPort(float)
        src_port4 = port.OutPort(bool)
        self.assertIsNone(chain.Chain(src_port2, dst_port1))
        self.assertIsNone(chain.Chain(src_port3, dst_port1))
        self.assertIsNone(chain.Chain(src_port4, dst_port1))

        dst_port2 = port.InPort(int)
        self.assertIsNotNone(chain.Chain(src_port2, dst_port2))
        self.assertIsNotNone(chain.Chain(src_port3, dst_port2))
        self.assertIsNotNone(chain.Chain(src_port4, dst_port2))

        dst_port3 = port.InPort(float)
        self.assertIsNotNone(chain.Chain(src_port2, dst_port3))
        self.assertIsNotNone(chain.Chain(src_port3, dst_port3))
        self.assertIsNotNone(chain.Chain(src_port4, dst_port3))

        dst_port4 = port.InPort(bool)
        self.assertIsNotNone(chain.Chain(src_port2, dst_port4))
        self.assertIsNotNone(chain.Chain(src_port3, dst_port4))
        self.assertIsNotNone(chain.Chain(src_port4, dst_port4))

    def test_connect(self):
        src_port1 = port.OutPort(str)
        dst_port1 = port.InPort(str)
        chan1 = chain.Chain(src_port1, dst_port1)
        self.assertIsNotNone(chan1)
        self.assertTrue(chan1.isConnected())

        src_port2 = port.OutPort(str)
        chan2 = chain.Chain(src_port2, dst_port1)
        self.assertIsNotNone(chan2)
        self.assertTrue(chan2.isConnected())
        self.assertFalse(chan1.isConnected())

        src_port3 = port.OutPort(int)
        chan3 = chain.Chain(src_port3, dst_port1)
        self.assertIsNone(chan3)
        self.assertTrue(chan2.isConnected())

        dst_port2 = port.InPort(bool)

        chan4 = chain.Chain(src_port3, dst_port2)
        self.assertIsNotNone(chan4)
        self.assertTrue(chan4.isConnected())

        src_port4 = port.OutPort(bool)

        chan5 = chain.Chain(src_port4, dst_port2)
        self.assertIsNotNone(chan5)
        self.assertTrue(chan5.isConnected())
        self.assertFalse(chan4.isConnected())

        dst_port3 = port.InPort(bool)
        chan6 = chain.Chain(src_port4, dst_port3)
        self.assertIsNotNone(chan6)
        self.assertTrue(chan6.isConnected())

        chan7 = chain.Chain(dst_port2, dst_port3)
        self.assertIsNone(chan7)

    def test_send(self):
        src_port = port.OutPort(str)
        dst_port = port.InPort(str)
        chain.Chain(src_port, dst_port)
        self.assertTrue(src_port.send("a"))
        self.assertFalse(dst_port.send("b"))

        self.assertFalse(src_port.send(1))
        self.assertFalse(src_port.send(True))
        self.assertFalse(src_port.send(1.2))

    def test_send_and_receive(self):
        src_port = port.OutPort(int)
        dst_port = port.InPort(int)
        chan1 = chain.Chain(src_port, dst_port)

        for i in range(5):
            self.assertTrue(src_port.send(i))

        pack1 = dst_port.receive()
        self.assertEqual(pack1.value(), 0)
        self.assertEqual(pack1.refCount(), 1)
        self.assertTrue(pack1.drop())

        self.assertEqual(dst_port.receive().value(), 1)
        self.assertEqual(dst_port.receive().value(), 2)
        self.assertEqual(dst_port.receive().value(), 3)
        self.assertEqual(dst_port.receive().value(), 4)
        self.assertIsNone(dst_port.receive())

    def test_send_and_receive2(self):
        src_port1 = port.OutPort(int)
        src_port2 = port.OutPort(int)
        dst_port = port.InPort(int)
        chan1 = chain.Chain(src_port1, dst_port)

        for i in range(5):
            self.assertTrue(src_port1.send(i))

        chan2 = chain.Chain(src_port2, dst_port)
        for i in range(5):
            self.assertFalse(src_port1.send(i))
            self.assertTrue(src_port2.send(i + 5))

        self.assertEqual(dst_port.receive().value(), 5)
        self.assertEqual(dst_port.receive().value(), 6)
        self.assertEqual(dst_port.receive().value(), 7)
        self.assertEqual(dst_port.receive().value(), 8)
        self.assertEqual(dst_port.receive().value(), 9)
        self.assertIsNone(dst_port.receive())

    def test_request(self):
        class TestComp(object):
            def __init__(self):
                self.__in = port.InPort(str, parent=self)
                self.__out = port.OutPort(str, parent=self)
                self.__is_terminated = False

            def inPort(self):
                return self.__in

            def outPort(self):
                return self.__out

            def run(self):
                if self.__is_terminated:
                    return

                self.__is_terminated = True
                for t in ["a", "b", "c"]:
                    self.__out.send(t)

        test_comp = TestComp()
        sp_chain = chain.Chain(test_comp.outPort(), test_comp.inPort())
        pc1 = test_comp.inPort().receive()
        self.assertIsNotNone(pc1)
        self.assertEqual(pc1.value(), "a")
        self.assertEqual(test_comp.inPort().receive().value(), "b")
        self.assertEqual(test_comp.inPort().receive().value(), "c")
        self.assertIsNone(test_comp.inPort().receive())
        self.assertIsNone(test_comp.inPort().receive())


if __name__ == "__main__":
    unittest.main()
