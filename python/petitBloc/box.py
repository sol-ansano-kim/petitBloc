from . import chain
from . import component
from . import util
from . import core
import copy


class ProxyBlock(core.Proxy, component.Component):
    In = 0
    Out = 1

    def __init__(self, direction, name="", parent=None):
        super(ProxyBlock, self).__init__(name=name, parent=parent)
        self.__ports = {}
        self.__direction = direction

    def isInProxy(self):
        return self.__direction is ProxyBlock.In

    def isOutProxy(self):
        return self.__direction is ProxyBlock.Out

    def proxies(self):
        return self.__ports.keys()

    def hasProxy(self, name):
        return self.__ports.has_key(name)

    def addProxy(self, typeClass, name=None):
        if name is None or not util.validateName(name):
            name = "proxy"

        all_names = self.__ports.keys()

        name = util.GetUniqueName(name, all_names)

        in_p = self.addInput(typeClass, name=name)
        out_p = self.addOutput(typeClass, name=name)

        if in_p is not None and out_p is not None:
            self.__ports[name] = {"in": in_p, "out": out_p, "end": False}
            return True

        return False

    def connect(self, name, port, isInside):
        chain_parent = None
        dst_chains = []
        proxy_port = None
        is_dst = False

        if self.__direction is ProxyBlock.In:
            if isInside:
                proxy_port = self.__ports[name]["out"]
                dst_chains = map(lambda x: x, port.chains())
                chain_parent = self.parent()
                is_dst = False
            else:
                proxy_port = self.__ports[name]["in"]
                dst_chains = map(lambda x: x, proxy_port.chains())
                chain_parent = port.parent().parent()
                is_dst = True
        else:
            if isInside:
                proxy_port = self.__ports[name]["in"]
                dst_chains = map(lambda x: x, proxy_port.chains())
                chain_parent = self.parent()
                is_dst = True
            else:
                proxy_port = self.__ports[name]["out"]
                dst_chains = map(lambda x: x, port.chains())
                chain_parent = port.parent().parent()
                is_dst = False

        if proxy_port is None or chain_parent is None:
            return False

        c = None
        if is_dst:
            c = chain.Chain(port, proxy_port)
        else:
            c = chain.Chain(proxy_port, port)

        if c:
            for dc in dst_chains:
                chain_parent.removeChain(dc)

        return chain_parent.addChain(c)

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


class Box(component.Component):
    def __init__(self, name="", parent=None):
        super(Box, self).__init__(name=name, parent=parent)
        self.__blocks = []
        self.__proxy_params = []
        self.__chains = []
        self.__in_proxy = ProxyBlock(ProxyBlock.In, name="inProxy", parent=self)
        self.__out_proxy = ProxyBlock(ProxyBlock.Out, name="outProxy", parent=self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Box<'{}'>".format(self.name())

    def chains(self):
        for c in self.__chains:
            yield c

    def chainCount(self):
        return len(self.__chains)

    def addChain(self, chain):
        if chain not in self.__chains:
            self.__chains.append(chain)
            return True

        return False

    def removeChain(self, chain):
        if chain in self.__chains:
            self.__chains.remove(chain)
            return True

        return False

    def getSchedule(self):
        schedule = []
        initblocs = []
        blocs = []

        schedule.append(self.__in_proxy)

        for bloc in self.__blocks:
            if filter(lambda x : x != self, bloc.upstream()):
                blocs.append(bloc)
                continue

            initblocs.append(bloc)

        for intbloc in initblocs:
            all_downstreams = []

            cur_blocs = [intbloc]
            while (cur_blocs):
                dns = []
                for b in cur_blocs:
                    all_downstreams += b.getSchedule()
                    dns += filter(lambda x : x in self.__blocks, b.downstream())

                cur_blocs = dns

            for db in all_downstreams:
                if db in blocs:
                    blocs.remove(db)
                schedule.append(db)

        for bloc in blocs:
            schedule.append(bloc.getSchedule())

        schedule.append(self.__out_proxy)

        return schedule

    def initialize(self):
        pass

    def blocks(self):
        for b in self.__blocks:
            yield b

    def blockCount(self):
        return len(self.__blocks)

    def addBlock(self, bloc):
        if bloc in self.__blocks:
            return False

        bloc.setParent(self)
        self.__blocks.append(bloc)
        return True

    def connect(self, srcPort, dstPort):
        src_block = srcPort.parent()
        dst_block = dstPort.parent()

        if src_block is None or dst_block is None:
            return False

        if src_block not in self.__blocks or dst_block not in self.__blocks:
            return False

        connected = []
        for dc in dstPort.chains():
            connected.append(dc)

        c = chain.Chain(srcPort, dstPort)
        if c is None:
            return False

        for dc in connected:
            self.removeChain(dc)

        self.addChain(c)

        return True

    def addProxyParam(self, param, name=None):
        for proxy in self.__proxy_params:
            if proxy.param() == param:
                return None

        if name is None or not util.validateName(name):
            name = param.name()

        all_names = map(lambda x: x.name(), self.__proxy_params)

        name = util.GetUniqueName(name, all_names)

        proxy = core.ProxyParameter(param, name)

        self.__proxy_params.append(proxy)

        return proxy

    def proxyParam(self, index_or_name):
        if isinstance(index_or_name, int):
            if index_or_name < 0 or index_or_name >= len(self.__proxy_params):
                return None

            return self.__proxy_params[index_or_name]

        if isinstance(index_or_name, basestring):
            for p in self.__proxy_params:
                if p.name() == index_or_name:
                    return p

        return None

    def removeProxyParam(self, proxy):
        if proxy in self.__proxy_params:
            self.__proxy_params.remove(proxy)
            return True

        return False

    def addInputProxy(self, typeClass, name=None):
        return self.__in_proxy.addProxy(typeClass, name=name)

    def addOutputProxy(self, typeClass, name=None):
        return self.__out_proxy.addProxy(typeClass, name=name)

    def inputProxy(self, name):
        return self.__in_proxy.input(name)

    def outputProxy(self, name):
        return self.__out_proxy.output(name)

    def hasInputProxy(self, name):
        return self.__in_proxy.hasProxy(name)

    def inputProxies(self):
        return self.__in_proxy.proxies()

    def hasOutputProxy(self, name):
        return self.__out_proxy.hasProxy(name)

    def outputProxies(self):
        return self.__out_proxy.proxies()

    def connectInputProxy(self, name, port):
        if not self.__in_proxy.hasProxy(name):
            return False

        port_block = port.parent()
        if not port_block:
            return False

        is_inside = port_block in self.__blocks
        if is_inside and not port.isInPort():
            return False

        if not is_inside and not port.isOutPort():
            return False

        return self.__in_proxy.connect(name, port, is_inside)

    def connectOutputProxy(self, name, port):
        if not self.__out_proxy.hasProxy(name):
            return False

        port_block = port.parent()
        if not port_block:
            return False

        is_inside = port_block in self.__blocks
        if is_inside and not port.isOutPort():
            return False

        if not is_inside and not port.isInPort():
            return False

        return self.__out_proxy.connect(name, port, is_inside)
