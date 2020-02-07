import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../python")))
from petitBloc import workerManager
from petitBloc import box
from petitBloc import block
import multiprocessing


class Sub(block.Block):
    def __init__(self):
        super(Sub, self).__init__()

    def initialize(self):
        pass

    def run(self):
        res = workerManager.SubmitSubProcess(os.path.abspath(os.path.join(__file__, "../sub")))
        res.result()
        for l in res.outputs():
            print(l)
        for l in res.errors():
            print(l)


class TestSubprocess(unittest.TestCase):
    def test_bloc(self):
        box1 = box.Box()
        for i in range(multiprocessing.cpu_count() * 3):
            box1.addBlock(Sub())

        self.assertTrue(workerManager.WorkerManager.RunSchedule(box1.getSchedule()))

        workerManager.WorkerManager.SetUseProcess(True)
        self.assertTrue(workerManager.WorkerManager.RunSchedule(box1.getSchedule()))



if __name__ == "__main__":
    unittest.main()
