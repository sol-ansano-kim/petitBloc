from petitBloc import block
from petitBloc import workerManager


class Shell(block.Block):
    def __init__(self):
        super(Shell, self).__init__()

    def initialize(self):
        self.addInput(str, "command")
        self.addOutput(bool, "result")
        self.addOutput(list, "out")
        self.addOutput(list, "err")

    def process(self):
        cmd_p = self.input("command").receive()
        if cmd_p.isEOP():
            return False

        cmd = cmd_p.value()
        cmd_p.drop()

        sp = workerManager.SubmitSubProcess(cmd)

        self.output("result").send(sp.result())
        self.output("out").send(sp.outputs())
        self.output("err").send(sp.errors())

        return True
