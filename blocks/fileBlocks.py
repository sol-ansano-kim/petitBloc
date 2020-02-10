from petitBloc import block
import os


class FileRead(block.Block):
    def __init__(self):
        super(FileRead, self).__init__()

    def initialize(self):
        self.addInput(str, "filePath")
        self.addOutput(str, "line")
        self.addOutput(list, "lines")

    def process(self):
        path_p = self.input("filePath").receive()
        if path_p.isEOP():
            return False

        path = path_p.value()
        path_p.drop()

        lines = []
        with open(path, "r") as f:
            for l in f.readlines():
                lines.append(l)
                self.output("line").send(l)

        self.output("lines").send(lines)

        return True


class FileWrite(block.Block):
    def __init__(self):
        super(FileWrite, self).__init__()

    def initialize(self):
        self.addInput(str, "filePath")
        self.addInput(list, "lines")
        self.addOutput(bool, "output")

    def process(self):
        path_p = self.input("filePath").receive()
        if path_p.isEOP():
            return False

        path = path_p.value()
        path_p.drop()

        lines_p = self.input("lines").receive()
        if lines_p.isEOP():
            return False

        lines = lines_p.value()
        lines_p.drop()

        dirname = os.path.dirname(path)

        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        with open(path, "w") as f:
            for d in lines:
                f.write(d)

        return True


class ListDir(block.Block):
    def __init__(self):
        super(ListDir, self).__init__()

    def initialize(self):
        self.addInput(str, "dirPath")
        self.addOutput(str, "file")
        self.addOutput(list, "files")
        self.addOutput(str, "directory")
        self.addOutput(list, "directories")

    def process(self):
        in_p = self.input("dirPath").receive()

        if in_p.isEOP():
            return False

        path = in_p.value()
        in_p.drop()

        files = []
        directories = []

        if os.path.isdir(path):
            for p in os.listdir(path):
                fp = os.path.abspath(os.path.join(path, p)).replace("\\", "/")

                if os.path.isdir(fp):
                    self.output("directory").send(fp)
                    directories.append(fp)
                else:
                    self.output("file").send(fp)
                    files.append(fp)

        self.output("directories").send(directories)
        self.output("files").send(files)

        return True
