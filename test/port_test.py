import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import port
from petitBloc import chain
from petitBloc import workerManager


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
        self.assertTrue(in_port.receive().isEOP())

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
        src_port.activate()
        self.assertTrue(src_port.send("a"))

        self.assertFalse(src_port.send(1))
        self.assertFalse(src_port.send(True))
        self.assertFalse(src_port.send(1.2))

    def test_send_and_receive(self):
        src_port = port.OutPort(int)
        dst_port = port.InPort(int)
        chan1 = chain.Chain(src_port, dst_port)
        src_port.activate()

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
        src_port1.activate()

        for i in range(5):
            self.assertTrue(src_port1.send(i))

        chan2 = chain.Chain(src_port2, dst_port)
        src_port1.terminate()
        src_port2.activate()

        for i in range(5):
            self.assertFalse(src_port1.send(i))
            self.assertTrue(src_port2.send(i + 5))

        self.assertEqual(dst_port.receive().value(), 5)
        self.assertEqual(dst_port.receive().value(), 6)
        self.assertEqual(dst_port.receive().value(), 7)
        self.assertEqual(dst_port.receive().value(), 8)
        self.assertEqual(dst_port.receive().value(), 9)
        self.assertTrue(chan2.empty())
        src_port2.terminate()

    def test_port_queue1(self):
        src_port1 = port.OutPort(int)
        dst_port = port.InPort(int)
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)
        src_port1.activate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 1)
        src_port1.terminate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)

        chan1 = chain.Chain(src_port1, dst_port)
        src_port1.activate()
        dst_port.activate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 3)
        src_port1.terminate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 2)
        dst_port.receive()
        dst_port.terminate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)

    def test_port_queue2(self):
        src_port1 = port.OutPort(int)
        src_port2 = port.OutPort(int)
        dst_port = port.InPort(int)
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)

        chan1 = chain.Chain(src_port1, dst_port)
        src_port1.activate()
        dst_port.activate()
        chan2 = chain.Chain(src_port2, dst_port)
        src_port2.activate()

        self.assertEqual(workerManager.WorkerManager.QueueCount(), 4)
        src_port1.terminate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 3)
        src_port2.terminate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 2)
        dst_port.receive()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 2)
        dst_port.terminate()
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)

    def test_packetInfo(self):
        src_port = port.OutPort(int)
        dst_port = port.InPort(int)

        chan = chain.Chain(src_port, dst_port)
        src_port.activate()
        dst_port.activate()
        src_port.send(1)
        src_port.send(2)
        dst_port.receive()
        src_port.terminate()
        dst_port.terminate()

        self.assertEqual(src_port.packetInfo(), [1, 2])
        self.assertEqual(dst_port.packetInfo(), [1])
        self.assertEqual(workerManager.WorkerManager.QueueCount(), 0)


if __name__ == "__main__":
    unittest.main()
