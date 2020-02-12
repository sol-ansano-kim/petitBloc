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


class PathDirname(block.Block):
    def __init__(self):
        super(PathDirname, self).__init__()

    def initialize(self):
        self.addInput(str, "filePath")
        self.addOutput(str, "dirname")

    def process(self):
        in_p = self.input("filePath").receive()

        if in_p.isEOP():
            return False

        path = in_p.value()
        in_p.drop()

        self.output("dirname").send(os.path.dirname(path))

        return True


class PathBasename(block.Block):
    def __init__(self):
        super(PathBasename, self).__init__()

    def initialize(self):
        self.addInput(str, "filePath")
        self.addOutput(str, "basename")

    def process(self):
        in_p = self.input("filePath").receive()

        if in_p.isEOP():
            return False

        path = in_p.value()
        in_p.drop()

        self.output("basename").send(os.path.basename(path))

        return True


class FileExtension(block.Block):
    def __init__(self):
        super(FileExtension, self).__init__()

    def initialize(self):
        self.addParam(bool, "keepDot", value=True)
        self.addInput(str, "filePath")
        self.addOutput(str, "extension")

    def process(self):
        in_p = self.input("filePath").receive()

        if in_p.isEOP():
            return False

        path = in_p.value()
        in_p.drop()

        ext = os.path.splitext(path)[1]
        if not self.param("keepDot").get() and ext.startswith("."):
            ext = ext[1:]

        self.output("extension").send(ext)

        return True


class FileSetExtension(block.Block):
    def __init__(self):
        super(FileSetExtension, self).__init__()

    def initialize(self):
        self.addInput(str, "inputPath")
        self.addInput(str, "extension")
        self.addOutput(str, "outputPath")

    def process(self):
        in_p = self.input("inputPath").receive()

        if in_p.isEOP():
            return False

        path = in_p.value()
        in_p.drop()

        in_e = self.input("extension").receive()

        if in_e.isEOP():
            return False

        ext = in_e.value()
        in_e.drop()

        if ext and not ext.startswith("."):
            ext = "." + ext

        self.output("outputPath").send(os.path.splitext(path)[0] + ext)

        return True


class PathJoin(block.Block):
    def __init__(self):
        super(PathJoin, self).__init__()

    def initialize(self):
        self.addInput(str, "dirName")
        self.addInput(str, "baseName")
        self.addOutput(str, "outputPath")

    def process(self):
        in_d = self.input("dirName").receive()

        if in_d.isEOP():
            return False

        dn = in_d.value()
        in_d.drop()

        in_b = self.input("baseName").receive()

        if in_b.isEOP():
            return False

        bn = in_b.value()
        in_b.drop()

        self.output("outputPath").send(os.path.join(dn, bn))

        return True
