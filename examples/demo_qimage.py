from petitBloc import block
from Qt import QtGui


class QImageRead(block.Block):
    def __init__(self):
        super(QImageRead, self).__init__()

    def initialize(self):
        self.addInput(str, "filepath")
        self.addOutput(QtGui.QImage, "qimage")

    def run(self):
        f_p = self.input("filepath").receive()
        if f_p.isEOP():
            return

        path = f_p.value()
        f_p.drop()

        self.output("qimage").send(QtGui.QImage(path))


class QImageIndices(block.Block):
    def __init__(self):
        super(QImageIndices, self).__init__()

    def initialize(self):
        self.addInput(QtGui.QImage, "qimage")
        self.addOutput(list, "index")

    def run(self):
        img_p = self.input("qimage").receive()
        if img_p.isEOP():
            return

        img = img_p.value()

        size = img.size()
        img_p.drop()

        out_p = self.output("index")
        for x in range(size.width()):
            for y in range(size.height()):
                out_p.send([x, y])


class QimageResized(block.Block):
    def __init__(self):
        super(QimageResized, self).__init__()

    def initialize(self):
        self.addInput(QtGui.QImage, "qimage")
        self.addInput(int, "width")
        self.addInput(int, "height")
        self.addOutput(QtGui.QImage, "scaled")

    def run(self):
        img_p = self.input("qimage").receive()
        if img_p.isEOP():
            return

        img = img_p.value()
        size = img.size()

        width_p = self.input("width").receive()
        if width_p.isEOP():
            return

        width = width_p.value()
        width_p.drop()

        height_p = self.input("height").receive()
        if height_p.isEOP():
            return

        height = height_p.value()
        height_p.drop()

        new_img = img.scaled(width, height)

        img_p.drop()

        self.output("scaled").send(new_img)


class QImagePixelColor(block.Block):
    def __init__(self):
        super(QImagePixelColor, self).__init__()

    def initialize(self):
        self.addInput(QtGui.QImage, "qimage")
        self.addInput(list, "index")
        self.addOutput(int, "r")
        self.addOutput(int, "g")
        self.addOutput(int, "b")

    def run(self):
        img_p = self.input("qimage").receive()
        if img_p.isEOP():
            return

        img = img_p.value()

        in_p = self.input("index")
        out_r = self.output("r")
        out_g = self.output("g")
        out_b = self.output("b")
        while (True):
            index_p = in_p.receive()
            if index_p.isEOP():
                break

            index = index_p.value()
            index_p.drop()

            rgb = img.pixelColor(index[0], index[1])
            out_r.send(rgb.red())
            out_g.send(rgb.green())
            out_b.send(rgb.blue())

        img_p.drop()


class QImageSize(block.Block):
    def __init__(self):
        super(QImageSize, self).__init__()

    def initialize(self):
        self.addInput(QtGui.QImage, "qimage")
        self.addOutput(int, "width")
        self.addOutput(int, "height")

    def process(self):
        img_p = self.input("qimage").receive()
        if img_p.isEOP():
            return False

        size = img_p.value().size()
        img_p.drop()

        self.output("width").send(size.width())
        self.output("height").send(size.height())

        return True
