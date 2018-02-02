from petitBloc import block
import os


class FileRead(block.Block):
    def __init__(self):
        super(FileRead, self).__init__()

    def initialize(self):
        self.addParam(str, "filePath")
        self.addOutput(str, "data")

    def run(self):
        path = self.param("filePath").get()
        if not os.path.isfile(path):
            return

        with open(path, "r") as f:
            for l in f.readlines():
                self.output("data").send(l)


class FileWrite(block.Block):
    def __init__(self):
        super(FileWrite, self).__init__()

    def initialize(self):
        self.addParam(str, "filePath")
        self.addInput(str, "data")

    def run(self):
        path = os.path.abspath(self.param("filePath").get())
        if not path:
            return

        dirname = os.path.dirname(path)

        if not dirname:
            return

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        in_port = self.input("data")
        datas = []
        while (True):
            package = in_port.receive()
            if package.isEOP():
                break

            datas.append(package.value())

        with open(path, "w") as f:
            for d in datas:
                f.write(d)
