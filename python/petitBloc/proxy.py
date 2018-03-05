from . import core
from . import component
from . import util
from . import chain
from . import packet


class ProxyChain(core.Proxy, chain.Chain):
    def __init__(self, srcPort, dstPort):
        super(ProxyChain, self).__init__(srcPort, dstPort)

    def activate(self):
        if self.dst() is None:
            return

        if not self.dst().isProxy():
            super(ProxyChain, self).activate()
            return

        for d in self.dst().proxyDestination():
            d.activate()

    def send(self, pack):
        if self.dst() is not None and self.dst().isProxy():
            return self.dst().carry(pack)

        return super(ProxyChain, self).send(pack)


class ProxyInPort(core.Proxy, core.PortIn, core.PortBase):
    def __init__(self, typeClass, name=None, parent=None):
        super(ProxyInPort, self).__init__(typeClass, name=name, parent=parent)
        self.__in_chain = None

    def isConnected(self):
        return self.__in_chain is not None

    def chains(self):
        if self.__in_chain is not None:
            yield self.__in_chain

    def connect(self, chn):
        if self.__in_chain:
            self.__in_chain.disconnect()

        self.__in_chain = chn

    def disconnect(self, chn):
        if self.__in_chain == chn:
            self.__in_chain = None

    def carry(self, pack):
        return self.parent().carry(pack)

    def proxySource(self):
        if self.__in_chain is None:
            return None

        src = self.__in_chain.src()
        if src is None:
            return None

        if not src.isProxy():
            return src

        return src.proxySource()

    def proxyDestination(self):
        return self.parent().proxyDestination()


class ProxyOutPort(core.Proxy, core.PortOut, core.PortBase):
    def __init__(self, typeClass, name=None, parent=None):
        super(ProxyOutPort, self).__init__(typeClass, name=name, parent=parent)
        self.__out_chains = []

    def isConnected(self):
        return len(self.__out_chains) > 0

    def chains(self):
        for c in self.__out_chains:
            yield c

    def connect(self, chn):
        if chn not in self.__out_chains:
            self.__out_chains.append(chn)

    def disconnect(self, chn):
        if chn in self.__out_chains:
            self.__out_chains.remove(chn)

    def send(self, pack):
        for c in self.__out_chains:
            c.send(pack)

    def proxySource(self):
        return self.parent().proxySource()

    def proxyDestination(self):
        destinations = []

        for c in self.__out_chains:
            dst = c.dst()

            if dst is None:
                continue

            if not dst.isProxy():
                destinations.append(dst)
                continue

            destinations += dst.proxyDestination()

        return destinations


class ProxyPort(core.Proxy, core.PortIn, core.PortOut, core.PortBase):
    def __init__(self, typeClass, name=None, parent=None):
        super(ProxyPort, self).__init__(typeClass, name=name, parent=parent)
        self.__in = ProxyInPort(typeClass, name="_in".format(self.name()), parent=self)
        self.__out = ProxyOutPort(typeClass, name="_out".format(self.name()), parent=self)

    def inPort(self):
        return self.__in

    def outPort(self):
        return self.__out

    def carry(self, pack):
        self.__out.send(pack)

    def proxySource(self):
        return self.__in.proxySource()

    def proxyDestination(self):
        return self.__out.proxyDestination()


class ProxyBlock(core.Proxy, component.Component):
    In = 0
    Out = 1

    def __init__(self, direction, name="", parent=None):
        super(ProxyBlock, self).__init__(name=name, parent=parent)
        self.__ports = []
        self.__direction = direction

    # def output(self, name):
    #     for pp in self.__ports:

    #         if pp["out"].name() == name:
    #             return pp["out"]

    #     return None

    # def input(self, name):
    #     for pp in self.__ports:
    #         if pp["in"].name() == name:
    #             return pp["in"]

    #     return None

    def hasConnection(self, port):
        for p in self.__ports:
            for c in p.inPort().chains():
                if c.src() == port:
                    return True
            for c in p.outPort().chains():
                if c.dst() == port:
                    return True

        return False

    def isInProxy(self):
        return self.__direction is ProxyBlock.In

    def isOutProxy(self):
        return self.__direction is ProxyBlock.Out

    def proxies(self):
        return self.__ports

    def hasProxy(self, name):
        for p in self.__ports:
            if p.name() == name:
                return True

        return False

    def proxyIn(self, name):
        for p in self.__ports:
            if p.name() == name:
                return p.inPort()

        return None

    def proxyOut(self, name):
        for p in self.__ports:
            if p.name() == name:
                return p.outPort()

        return None

    # def proxyName(self, port):
    #     for name, ports in self.__ports.iteritems():
    #         if ports["in"] == port:
    #             return name
    #         if ports["out"] == port:
    #             return name

    #     return None

    def getContext(self):
        return {}

    def addProxy(self, typeClass, name=None):
        if name is None or not util.ValidateName(name):
            name = "proxy"

        all_names = map(lambda x: x.name(), self.__ports)

        name = util.GetUniqueName(name, all_names)

        p = ProxyPort(typeClass, name=name)
        self.__ports.append(p)

        return p

    def removeProxy(self, name):
        port = None
        for p in self.__ports:
            if p.name() == name:
                port = p
                break

        if not port:
            return False

        self.__ports.remove(port)

        for c in port.inPort().chains():
            c.disconnect()

        for c in port.outPort().chains():
            c.disconnect()

        return True

    def activate(self):
        super(ProxyBlock, self).activate()
        for port in self.__ports:
            port.activate()
