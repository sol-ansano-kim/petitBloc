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
        in_port1 = port.InPort(str)
        out_port1 = port.OutPort(str)
        self.assertIsNotNone(chain.Chain(in_port1, out_port1))
        self.assertIsNone(chain.Chain(out_port1, in_port1))
        self.assertIsNone(chain.Chain(out_port1, out_port1))
        self.assertIsNone(chain.Chain(in_port1, in_port1))

        in_port2 = port.InPort(int)
        in_port3 = port.InPort(float)
        in_port4 = port.InPort(bool)
        self.assertIsNone(chain.Chain(in_port2, out_port1))
        self.assertIsNone(chain.Chain(in_port3, out_port1))
        self.assertIsNone(chain.Chain(in_port4, out_port1))

        out_port2 = port.OutPort(int)
        self.assertIsNotNone(chain.Chain(in_port2, out_port2))
        self.assertIsNotNone(chain.Chain(in_port3, out_port2))
        self.assertIsNotNone(chain.Chain(in_port4, out_port2))

        out_port3 = port.OutPort(float)
        self.assertIsNotNone(chain.Chain(in_port2, out_port3))
        self.assertIsNotNone(chain.Chain(in_port3, out_port3))
        self.assertIsNotNone(chain.Chain(in_port4, out_port3))

        out_port4 = port.OutPort(bool)
        self.assertIsNotNone(chain.Chain(in_port2, out_port4))
        self.assertIsNotNone(chain.Chain(in_port3, out_port4))
        self.assertIsNotNone(chain.Chain(in_port4, out_port4))

    def test_connect(self):
        in_port1 = port.InPort(str)
        out_port1 = port.OutPort(str)
        chan1 = chain.Chain(in_port1, out_port1)
        self.assertIsNotNone(chan1)
        self.assertTrue(chan1.isConnected())

        in_port2 = port.InPort(str)
        chan2 = chain.Chain(in_port2, out_port1)
        self.assertIsNotNone(chan2)
        self.assertTrue(chan2.isConnected())
        self.assertFalse(chan1.isConnected())

        in_port3 = port.InPort(int)
        chan3 = chain.Chain(in_port3, out_port1)
        self.assertIsNone(chan3)
        self.assertTrue(chan2.isConnected())

        out_port2 = port.OutPort(bool)

        chan4 = chain.Chain(in_port3, out_port2)
        self.assertIsNotNone(chan4)
        self.assertTrue(chan4.isConnected())

        in_port4 = port.InPort(bool)

        chan5 = chain.Chain(in_port4, out_port2)
        self.assertIsNotNone(chan5)
        self.assertTrue(chan5.isConnected())
        self.assertFalse(chan4.isConnected())

        out_port3 = port.OutPort(bool)
        chan6 = chain.Chain(in_port4, out_port3)
        self.assertIsNotNone(chan6)
        self.assertTrue(chan6.isConnected())

        chan7 = chain.Chain(out_port2, out_port3)
        self.assertIsNone(chan7)

    def test_send(self):
        in_port = port.InPort(str)
        out_port = port.OutPort(str)
        chain.Chain(in_port, out_port)
        self.assertTrue(in_port.send("a"))
        self.assertFalse(out_port.send("b"))

        self.assertFalse(in_port.send(1))
        self.assertFalse(in_port.send(True))
        self.assertFalse(in_port.send(1.2))

    def test_send_and_receive(self):
        in_port = port.InPort(int)
        out_port = port.OutPort(int)
        chan1 = chain.Chain(in_port, out_port)

        for i in range(5):
            self.assertTrue(in_port.send(i))

        pack1 = out_port.receive()
        self.assertEqual(pack1.value(), 0)
        self.assertEqual(pack1.refCount(), 1)
        self.assertTrue(pack1.drop())

        self.assertEqual(out_port.receive().value(), 1)
        self.assertEqual(out_port.receive().value(), 2)
        self.assertEqual(out_port.receive().value(), 3)
        self.assertEqual(out_port.receive().value(), 4)
        self.assertIsNone(out_port.receive())

    def test_send_and_receive2(self):
        in_port1 = port.InPort(int)
        in_port2 = port.InPort(int)
        out_port = port.OutPort(int)
        chan1 = chain.Chain(in_port1, out_port)

        for i in range(5):
            self.assertTrue(in_port1.send(i))

        chan2 = chain.Chain(in_port2, out_port)
        for i in range(5):
            self.assertFalse(in_port1.send(i))
            self.assertTrue(in_port2.send(i + 5))

        self.assertEqual(out_port.receive().value(), 5)
        self.assertEqual(out_port.receive().value(), 6)
        self.assertEqual(out_port.receive().value(), 7)
        self.assertEqual(out_port.receive().value(), 8)
        self.assertEqual(out_port.receive().value(), 9)
        self.assertIsNone(out_port.receive())

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
                    self.__in.send(t)

        test_comp = TestComp()
        sp_chain = chain.Chain(test_comp.inPort(), test_comp.outPort())
        pc1 = test_comp.outPort().receive()
        self.assertIsNotNone(pc1)
        self.assertEqual(pc1.value(), "a")
        self.assertEqual(test_comp.outPort().receive().value(), "b")
        self.assertEqual(test_comp.outPort().receive().value(), "c")
        self.assertIsNone(test_comp.outPort().receive())
        self.assertIsNone(test_comp.outPort().receive())


if __name__ == "__main__":
    unittest.main()
