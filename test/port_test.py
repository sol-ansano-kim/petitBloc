import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import port
from petitBloc import chain


class PortTest(unittest.TestCase):
    def test_init(self):
        in_port = port.InPort(str)
        out_port = port.OutPort(str)
        self.assertIsNotNone(in_port)
        self.assertIsNotNone(out_port)

    def test_send(self):
        out_port = port.OutPort(str)
        self.assertFalse(out_port.send("a"))

    def test_receive(self):
        in_port = port.InPort(str)
        self.assertIsNone(in_port.receive())

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
        self.assertFalse(chan1.closed())

        src_port2 = port.OutPort(str)
        chan2 = chain.Chain(src_port2, dst_port1)
        self.assertIsNotNone(chan2)
        self.assertFalse(chan2.closed())
        self.assertTrue(chan1.closed())

        src_port3 = port.OutPort(int)
        chan3 = chain.Chain(src_port3, dst_port1)
        self.assertIsNone(chan3)
        self.assertFalse(chan2.closed())

        dst_port2 = port.InPort(bool)

        chan4 = chain.Chain(src_port3, dst_port2)
        self.assertIsNotNone(chan4)
        self.assertFalse(chan4.closed())

        src_port4 = port.OutPort(bool)

        chan5 = chain.Chain(src_port4, dst_port2)
        self.assertIsNotNone(chan5)
        self.assertFalse(chan5.closed())
        self.assertTrue(chan4.closed())

        dst_port3 = port.InPort(bool)
        chan6 = chain.Chain(src_port4, dst_port3)
        self.assertIsNotNone(chan6)
        self.assertFalse(chan6.closed())

        chan7 = chain.Chain(dst_port2, dst_port3)
        self.assertIsNone(chan7)

    def test_send(self):
        src_port = port.OutPort(str)
        dst_port = port.InPort(str)
        chain.Chain(src_port, dst_port)
        self.assertTrue(src_port.send("a"))

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
        self.assertTrue(chan1.empty())

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
        self.assertTrue(chan2.empty())


if __name__ == "__main__":
    unittest.main()
