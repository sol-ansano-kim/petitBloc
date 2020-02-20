from petitBloc import block
from petitBloc import workerManager
import OpenImageIO
import os


class ListDir(block.Block):
    def __init__(self):
        super(ListDir, self).__init__()

    def initialize(self):
        self.addInput(str, "directory")
        self.addOutput(str, "file")
        self.addOutput(str, "subDir")

    def process(self):
        di_p = self.input("directory").receive()
        if di_p.isEOP():
            return False

        di_v = di_p.value()
        di_p.drop()

        if not os.path.isdir(di_v):
            return True

        for p in os.listdir(di_v):
            path = os.path.join(di_v, p)
            if os.path.isfile(path):
                self.output("file").send(path)

            elif os.path.isdir(path):
                self.output("subDir").send(path)

        return True


class DirName(block.Block):
    def __init__(self):
        super(DirName, self).__init__()

    def initialize(self):
        self.addInput(str, "path")
        self.addOutput(str, "dirname")

    def process(self):
        p_p = self.input("path").receive()
        if p_p.isEOP():
            return False

        self.output("dirname").send(os.path.dirname(p_p.value()))
        p_p.drop()

        return True


class BaseName(block.Block):
    def __init__(self):
        super(BaseName, self).__init__()

    def initialize(self):
        self.addInput(str, "path")
        self.addOutput(str, "basename")

    def process(self):
        p_p = self.input("path").receive()
        if p_p.isEOP():
            return False

        self.output("basename").send(os.path.basename(p_p.value()))
        p_p.drop()

        return True


class SplitExt(block.Block):
    def __init__(self):
        super(SplitExt, self).__init__()

    def initialize(self):
        self.addInput(str, "path")
        self.addOutput(str, "base")
        self.addOutput(str, "ext")

    def process(self):
        p_p = self.input("path").receive()
        if p_p.isEOP():
            return False

        base, ext = os.path.splitext(p_p.value())
        p_p.drop()

        self.output("base").send(base)
        self.output("ext").send(ext)

        return True


class Join(block.Block):
    def __init__(self):
        super(Join, self).__init__()

    def initialize(self):
        self.addInput(str, "input1")
        self.addInput(str, "input2")
        self.addOutput(str, "path")

    def run(self):
        self.__in1_eop = False
        self.__in1 = None
        self.__in2_eop = False
        self.__in2 = None

        super(Join, self).run()

    def process(self):
        if not self.__in1_eop:
            in1_p = self.input("input1").receive()
            if in1_p.isEOP():
                self.__in1_eop = True
            else:
                self.__in1 = in1_p.value()
                in1_p.drop()

        if self.__in1 is None:
            return False

        if not self.__in2_eop:
            in2_p = self.input("input2").receive()
            if in2_p.isEOP():
                self.__in2_eop = True
            else:
                self.__in2 = in2_p.value()
                in2_p.drop()

        if self.__in2 is None:
            return False

        if self.__in1_eop and self.__in2_eop:
            return False

        self.output("path").send(os.path.join(self.__in1, self.__in2))

        return True


class MakeDirs(block.Block):
    def __init__(self):
        super(MakeDirs, self).__init__()

    def initialize(self):
        self.addInput(str, "path")

    def process(self):
        path_p = self.input("path").receive()
        if path_p.isEOP():
            return False

        path = path_p.value()
        path_p.drop()

        if not os.path.isdir(path):
            os.makedirs(path)

        return True


class OIIOImageRead(block.Block):
    def __init__(self):
        super(OIIOImageRead, self).__init__()

    def initialize(self):
        self.addInput(str, "path")
        self.addOutput(OpenImageIO.ImageBuf, "image")

    def process(self):
        path_p = self.input("path").receive()
        if path_p.isEOP():
            return False

        self.output("image").send(OpenImageIO.ImageBuf(path_p.value()))
        path_p.drop()

        return True


class OIIOImageSize(block.Block):
    def __init__(self):
        super(OIIOImageSize, self).__init__()

    def initialize(self):
        self.addInput(OpenImageIO.ImageBuf, "image")
        self.addOutput(int, "width")
        self.addOutput(int, "height")

    def process(self):
        img_p = self.input("image").receive()
        if img_p.isEOP():
            return False

        spec = img_p.value().spec()
        w = spec.width
        h = spec.height

        img_p.drop()

        self.output("width").send(w)
        self.output("height").send(h)

        return True


class OIIOImageWrite(block.Block):
    def __init__(self):
        super(OIIOImageWrite, self).__init__()

    def initialize(self):
        self.addInput(OpenImageIO.ImageBuf, "image")
        self.addInput(str, "path")
        self.addOutput(str, "outFile")

    def process(self):
        img_p = self.input("image").receive()
        if img_p.isEOP():
            return False

        img = img_p.value()
        img_p.drop()

        path_p = self.input("path").receive()
        if path_p.isEOP():
            return False

        path = path_p.value()
        path_p.drop()

        img.write(path)

        self.output("outFile").send(path)

        return True


class OIIOImageResize(block.Block):
    def __init__(self):
        super(OIIOImageResize, self).__init__()

    def initialize(self):
        self.addInput(OpenImageIO.ImageBuf, "image")
        self.addInput(int, "width")
        self.addInput(int, "height")
        self.addOutput(OpenImageIO.ImageBuf, "resized")

    def process(self):
        ip = self.input("image").receive()
        if ip.isEOP():
            return False

        org = ip.value()

        w_p = self.input("width").receive()
        if w_p.isEOP():
            return False

        w = w_p.value()
        w_p.drop()

        h_p = self.input("height").receive()
        if h_p.isEOP():
            return False

        h = h_p.value()
        h_p.drop()

        spec = org.spec()
        new = OpenImageIO.ImageBuf(OpenImageIO.ImageSpec(w, h, spec.nchannels, spec.format.basetype))
        OpenImageIO.ImageBufAlgo.resize(new, org)
        ip.drop()

        self.output("resized").send(new)

        return True


class MakeTx(block.Block):
    def __init__(self):
        super(MakeTx, self).__init__()

    def initialize(self):
        self.addInput(str, "inImage")
        self.addInput(str, "outImage")
        self.addInput(str, "inColorspace")
        self.addInput(str, "outColorspace")
        self.addOutput(bool, "result")

    def run(self):
        self.__in_col_eop = False
        self.__out_col_eop = False
        self.__in_col = None
        self.__out_col = None

        super(MakeTx, self).run()

    def process(self):
        if not self.__in_col_eop:
            inc = self.input("inColorspace").receive()
            if inc.isEOP():
                self.__in_col_eop = True
            else:
                self.__in_col = inc.value()

        if self.__in_col is None:
            return False

        if not self.__out_col_eop:
            outc = self.input("outColorspace").receive()
            if outc.isEOP():
                self.__out_col_eop = True
            else:
                self.__out_col = outc.value()

        if self.__out_col is None:
            return False

        in_p = self.input("inImage").receive()
        if in_p.isEOP():
            return False

        in_i = in_p.value()
        in_p.drop()

        out_p = self.input("outImage").receive()
        if out_p.isEOP():
            return False

        out_i = out_p.value()
        out_p.drop()

        cmd = 'maketx -o "{outImage}" -colorconvert {inColorspace} {outColorspace} "{inImage}"'.format(outImage=out_i, inImage=in_i, inColorspace=self.__in_col, outColorspace=self.__out_col)

        self.debug(cmd)
        res = workerManager.SubmitSubProcess(cmd)

        self.output("result").send(res.result())

        return True
