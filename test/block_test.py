import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import block
from petitBloc import chain
import threading
import Queue
import time


class MakeString(block.Block):
    def __init__(self):
        super(MakeString, self).__init__()

    def initialize(self):
        self.addOutput(str)

    def process(self):
        self.output(0).send("Hello World. My Name is MakeString")
        time.sleep(0.01)
        return False


class SplitString(block.Block):
    def __init__(self):
        super(SplitString, self).__init__()

    def initialize(self):
        self.addInput(str, "input")
        self.addOutput(str, "output")

    def process(self):
        pack = self.input(0).receive()
        if pack.isEOP():
            return False

        output = self.output(0)
        for txt in pack.value().split(" "):
            output.send(txt)
            time.sleep(0.01)

        pack.drop()

        return True


class DumpString(block.Block):
    def __init__(self):
        super(DumpString, self).__init__()
        self.dmp = Queue.Queue()
        self.lst = []
        self.count = 0

    def initialize(self):
        self.addInput(str, "string")

    def process(self):
        pack = self.input(0).receive()
        if pack.isEOP():
            return False

        self.count += 1
        self.lst.append(pack.value())
        self.dmp.put(pack.value())
        pack.drop()

        return True


class PacketTest(unittest.TestCase):
    def test_init(self):
        blck = block.Block(name="a")
        self.assertIsNotNone(blck)
        self.assertEqual(blck.__str__(), "Block<'a'>")

    def test_add_port(self):
        blck = block.Block()
        in1 = blck.addInput(str)
        self.assertIsNotNone(in1)
        self.assertEqual(in1.name(), "input")

        in2 = blck.addInput(int)
        self.assertIsNotNone(in2)
        self.assertEqual(in2.name(), "input1")

        in3 = blck.addInput(int, "test")
        self.assertIsNotNone(in3)
        self.assertEqual(in3.name(), "test")

        in4 = blck.addInput(int, "test")
        self.assertIsNotNone(in4)
        self.assertEqual(in4.name(), "test1")

        out1 = blck.addOutput(str)
        self.assertIsNotNone(out1)
        self.assertEqual(out1.name(), "output")

        out2 = blck.addOutput(int)
        self.assertIsNotNone(out2)
        self.assertEqual(out2.name(), "output1")

        out3 = blck.addOutput(int, "test")
        self.assertIsNotNone(out3)
        self.assertEqual(out3.name(), "test2")

        out4 = blck.addOutput(int, "test")
        self.assertIsNotNone(out4)
        self.assertEqual(out4.name(), "test3")

    def test_custom_block(self):
        ms = MakeString()
        ss = SplitString()
        ps = DumpString()
        c1 = chain.Chain(ms.output(0), ss.input(0))
        self.assertIsNotNone(c1)
        c2 = chain.Chain(ss.output(0), ps.input(0))
        self.assertIsNotNone(c2)
        ms.activate()
        ms.run()
        ms.terminate()
        ss.activate()
        ss.run()
        ss.terminate()
        ps.activate()
        ps.run()
        ps.terminate()

        self.assertEqual(ps.lst, ['Hello', 'World.', 'My', 'Name', 'is', 'MakeString'])

    def test_custom_block2(self):
        ms = MakeString()
        ss = SplitString()
        ps = DumpString()
        c1 = chain.Chain(ms.output(0), ss.input(0))
        self.assertIsNotNone(c1)
        c2 = chain.Chain(ss.output(0), ps.input(0))
        self.assertIsNotNone(c2)

        processes = []
        ps.activate()
        p = threading.Thread(target=ps.run)
        p.daemon = True
        p.start()
        processes.append((p, ps))

        ss.activate()
        p = threading.Thread(target=ss.run)
        p.daemon = True
        p.start()
        processes.append((p, ss))

        ms.activate()
        p = threading.Thread(target=ms.run)
        p.daemon = True
        p.start()
        processes.append((p, ms))

        while (True):
            working = False
            for p, b in processes:
                if p.is_alive():
                    working = True
                else:
                    if not b.isTerminated():
                        b.terminate()

            if working is False:
                break

        result = []
        while (not ps.dmp.empty()):
            result.append(ps.dmp.get())
        self.assertEqual(result, ['Hello', 'World.', 'My', 'Name', 'is', 'MakeString'])


if __name__ == "__main__":
    unittest.main()
