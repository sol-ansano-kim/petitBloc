import os
import datetime
from maya import cmds
from maya import OpenMayaUI
from maya import OpenMaya
from petitBloc.exts import mayaExts
from petitBloc import block


class MayaCreateParticle(block.Block):
    def __init__(self):
        super(MayaCreateParticle, self).__init__()

    def initialize(self):
        self.addInput(float, "x")
        self.addInput(float, "y")
        self.addInput(float, "z")
        self.addInput(float, "r")
        self.addInput(float, "g")
        self.addInput(float, "b")

    def __run(self, *args, **kwargs):
        pos = kwargs.get("position", [])
        col = kwargs.pop("color", [])

        particle = cmds.particle(**kwargs)[1]

        if col and len(col) == len(pos):
            cmds.addAttr(particle, ln="rgbPP", dt="vectorArray")
            cmds.addAttr(particle, ln="rgbPP0", dt="vectorArray")
            color_exp = "vector $vectorList[] = {%s};" % (",".join(map(lambda x : "<<{},{},{}>>".format(x[0], x[1], x[2]), col)))
            color_exp += "\nint $id = id;\n%s.rgbPP = $vectorList[$id];" % (particle)
            cmds.dynExpression(particle, c=1, s=color_exp)

        return particle

    def run(self):
        positions = []
        in_x = self.input("x")
        in_y = self.input("y")
        in_z = self.input("z")

        while (True):
            xp = in_x.receive()
            if xp.isEOP():
                break
            x = xp.value()
            xp.drop()

            yp = in_y.receive()
            if yp.isEOP():
                break
            y = yp.value()
            yp.drop()

            zp = in_z.receive()
            if zp.isEOP():
                break
            z = zp.value()
            zp.drop()

            positions.append((x, y, z))

        colors = []
        in_r = self.input("r")
        in_g = self.input("g")
        in_b = self.input("b")

        while (True):
            rp = in_r.receive()
            if rp.isEOP():
                break
            r = rp.value()
            rp.drop()

            gp = in_g.receive()
            if gp.isEOP():
                break
            g = gp.value()
            gp.drop()

            bp = in_b.receive()
            if bp.isEOP():
                break
            b = bp.value()
            bp.drop()

            colors.append((r, g, b))

        mayaExts.ExecuteFunction(self.__run, position=positions, color=colors)


class CurrentTime(block.Block):
    def __init__(self):
        super(CurrentTime, self).__init__()

    def initialize(self):
        self.addOutput(str, "time")

    def run(self):
        self.output("time").send(datetime.datetime.today().strftime("%Y%m%d_%H%M%S"))


class MayaSnapShot(block.Block):
    def __init__(self):
        super(MayaSnapShot, self).__init__()

    def initialize(self):
        self.addInput(str, "filePath")
        self.addOutput(str, "outImage")

    def __run(self, *args, **kwargs):
        img = OpenMaya.MImage()
        view = OpenMayaUI.M3dView_active3dView()
        view.readColorBuffer(img, True)
        img.writeToFile(args[0], os.path.splitext(args[0])[-1][1:])

        return True

    def run(self):
        path_p = self.input("filePath").receive()
        if path_p.isEOP():
            return

        path = path_p.value()
        path_p.drop()

        mayaExts.ExecuteFunction(self.__run, path)

        self.output("outImage").send(path)
