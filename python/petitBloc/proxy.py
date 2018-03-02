from . import core
from . import component
from . import util


class ProxyBlock(core.Proxy, component.Component):
    In = 0
    Out = 1

    def __init__(self, direction, name="", parent=None):
        super(ProxyBlock, self).__init__(name=name, parent=parent)
        self.__ports = {}
        self.__direction = direction

    def output(self, name):
        for pp in self.__ports.values():
            if pp["out"].name() == name:
                return pp["out"]

        return None

    def input(self, name):
        for pp in self.__ports.values():
            if pp["in"].name() == name:
                return pp["in"]

        return None

    def hasConnection(self, port):
        if self.isInProxy():
            for o in self.outputs():
                for c in o.chains():
                    if c.dst() == port:
                        return True
        else:
            for i in self.outputs():
                for c in i.chains():
                    if c.src() == port:
                        return True

        return False

    def isInProxy(self):
        return self.__direction is ProxyBlock.In

    def isOutProxy(self):
        return self.__direction is ProxyBlock.Out

    def proxies(self):
        return self.__ports.keys()

    def hasProxy(self, name):
        return self.__ports.has_key(name)

    def proxyIn(self, name):
        return self.__ports.get(name, {}).get("in")

    def proxyOut(self, name):
        return self.__ports.get(name, {}).get("out")

    def proxyName(self, port):
        for name, ports in self.__ports.iteritems():
            if ports["in"] == port:
                return name
            if ports["out"] == port:
                return name

        return None

    def getContext(self):
        return {}

    def addProxy(self, typeClass, name=None):
        if name is None or not util.ValidateName(name):
            name = "proxy"

        all_names = self.__ports.keys()

        name = util.GetUniqueName(name, all_names)

        in_p = self.addInput(typeClass, name=name + "_in")
        out_p = self.addOutput(typeClass, name=name + "_out")

        if in_p is not None and out_p is not None:
            self.__ports[name] = {"in": in_p, "out": out_p, "end": False}
            return (in_p, out_p)

        return (in_p, out_p)

    def removeProxy(self, name):
        ports = self.__ports.pop(name, {})
        if not ports:
            return False

        if self.__direction is ProxyBlock.In:
            for c in ports["in"].chains():
                c.src().parent().removeChain(c)
                c.disconnect()
            for c in ports["out"].chains():
                self.parent().removeChain(c)
                c.disconnect()

            self.removeInput(ports["in"])
            self.removeOutput(ports["out"])

        else:
            for c in ports["in"].chains():
                self.parent().removeChain(c)
                c.disconnect()
            for c in ports["out"].chains():
                c.src().parent().removeChain(c)
                c.disconnect()

            self.removeInput(ports["in"])
            self.removeOutput(ports["out"])

        return True

    def activate(self):
        super(ProxyBlock, self).activate()
        for values in self.__ports.values():
            values["end"] = False

    def process(self):
        keep = False
        for values in self.__ports.values():
            if values["end"]:
                continue

            keep = True
            p = values["in"].receive()

            if p.isEOP():
                values["end"] = True
                continue

            values["out"].send(p.value())

        return keep
