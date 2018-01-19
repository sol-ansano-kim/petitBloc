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

    def addProxy(self, typeClass, name=None):
        if name is None or not util.ValidateName(name):
            name = "proxy"

        all_names = self.__ports.keys()

        name = util.GetUniqueName(name, all_names)

        in_p = self.addInput(typeClass, name=name + "In")
        out_p = self.addOutput(typeClass, name=name + "Out")

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
        else:
            for c in ports["in"].chains():
                self.parent().removeChain(c)
                c.disconnect()
            for c in ports["out"].chains():
                c.src().parent().removeChain(c)
                c.disconnect()

        return True

    def disconnect(self, name, port, isInside):
        chain_parent = None
        remove_chain = None

        if self.__direction is ProxyBlock.In:
            if isInside:
                for dst in port.chains():
                    if dst.src() == self.__ports[name]["out"]:
                        remove_chain = dst
                        break

                chain_parent = self.parent()

            else:
                for dst in self.__ports[name]["in"].chains():
                    if dst.src() == port:
                        remove_chain = dst
                        break

                chain_parent = port.parent().parent()

        else:
            if isInside:
                for dst in self.__ports[name]["in"].chains():
                    if dst.src() == port:
                        remove_chain = dst
                        break

                chain_parent = self.parent()

            else:
                for dst in port.chains():
                    if dst.src() == self.__ports[name]["out"]:
                        remove_chain = dst
                        break

                chain_parent = port.parent().parent()

        if chain_parent is None or remove_chain is None:
            return True

        remove_chain.disconnect()

        return chain_parent.removeChain(remove_chain)

    def connect(self, name, port, isInside):
        chain_parent = None
        dst_chains = []
        proxy_port = None
        is_dst = False

        if self.__direction is ProxyBlock.In:
            if isInside:
                proxy_port = self.__ports[name]["out"]
                dst_chains = map(lambda x: x, port.chains())
                for dst in dst_chains:
                    if dst.src() == proxy_port:
                        return True

                chain_parent = self.parent()
                is_dst = False
            else:
                proxy_port = self.__ports[name]["in"]
                dst_chains = map(lambda x: x, proxy_port.chains())
                for dst in dst_chains:
                    if dst.src() == port:
                        return True

                chain_parent = port.parent().parent()
                is_dst = True
        else:
            if isInside:
                proxy_port = self.__ports[name]["in"]
                dst_chains = map(lambda x: x, proxy_port.chains())
                for dst in dst_chains:
                    if dst.src() == port:
                        return True

                chain_parent = self.parent()
                is_dst = True
            else:
                proxy_port = self.__ports[name]["out"]
                dst_chains = map(lambda x: x, port.chains())
                for dst in dst_chains:
                    if dst.src() == proxy_port:
                        return True

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
        self.__in_proxy = ProxyBlock(ProxyBlock.In, name="in", parent=self)
        self.__out_proxy = ProxyBlock(ProxyBlock.Out, name="out", parent=self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Box<'{}'>".format(self.name())

    def hasNetwork(self):
        return True

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
        schedule.append(self)

        return schedule

    def initialize(self):
        pass

    def blocks(self):
        for b in self.__blocks:
            yield b

    def blockCount(self):
        return len(self.__blocks)

    def getUniqueName(self, bloc, name):
        if not name or not util.ValidateName(name):
            name = bloc.__class__.__name__

        all_names = ["in", "out"] + map(lambda x: x.name(), filter(lambda y: y != bloc, self.__blocks))

        return util.GetUniqueName(name, all_names)

    def addBlock(self, bloc):
        if bloc in self.__blocks:
            return False

        bloc.rename(self.getUniqueName(bloc, bloc.name()))
        bloc.setParent(self)
        self.__blocks.append(bloc)
        return True

    def deleteBlock(self, bloc):
        if bloc not in self.__blocks:
            return False

        self.__blocks.remove(bloc)
        bloc.setParent(None)

        for ip in bloc.inputs():
            for c in ip.chains():
                c.disconnect()
                self.removeChain(c)

        for op in bloc.inputs():
            for c in op.chains():
                c.disconnect()
                self.removeChain(c)

        return True

    def isConnected(self, srcPort, dstPort):
        src_block = srcPort.parent()
        dst_block = dstPort.parent()

        if src_block is None or dst_block is None:
            return False

        if src_block not in self.__blocks or dst_block not in self.__blocks:
            return False

        dst_chain = None
        for c in dstPort.chains():
            dst_chain = c

        if dst_chain is None:
            return False

        return dst_chain.src() == srcPort

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

    def disconnect(self, srcPort, dstPort):
        src_block = srcPort.parent()
        dst_block = dstPort.parent()

        if src_block is None or dst_block is None:
            return False

        if src_block not in self.__blocks or dst_block not in self.__blocks:
            return False

        dst_chain = None
        for c in dstPort.chains():
            dst_chain = c

        if dst_chain is None:
            return False

        if dst_chain.src() != srcPort:
            return False

        dst_chain.disconnect()
        self.removeChain(dst_chain)

        return True

    def addProxyParam(self, param, name=None):
        for proxy in self.__proxy_params:
            if proxy.param() == param:
                return None

        if name is None or not util.ValidateName(name):
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

    def removeInputProxyPort(self, proxyPort):
        name = self.__in_proxy.proxyName(proxyPort)
        if name is None:
            return False

        return self.removeInputProxy(name)

    def removeOutputProxyPort(self, proxyPort):
        name = self.__out_proxy.proxyName(proxyPort)
        if name is None:
            return False

        return self.removeOutputProxy(name)

    def removeInputProxy(self, name):
        return self.__in_proxy.removeProxy(name)

    def removeOutputProxy(self, name):
        return self.__out_proxy.removeProxy(name)

    def inProxyBlock(self):
        return self.__in_proxy

    def outProxyBlock(self):
        return self.__out_proxy

    def inputProxyIn(self, name):
        return self.__in_proxy.proxyIn(name)

    def inputProxyOut(self, name):
        return self.__in_proxy.proxyOut(name)

    def outputProxyIn(self, name):
        return self.__out_proxy.proxyIn(name)

    def outputProxyOut(self, name):
        return self.__out_proxy.proxyOut(name)

    def hasInputProxy(self, name):
        return self.__in_proxy.hasProxy(name)

    def inputProxies(self):
        return self.__in_proxy.proxies()

    def hasOutputProxy(self, name):
        return self.__out_proxy.hasProxy(name)

    def outputProxies(self):
        return self.__out_proxy.proxies()

    def connectInputProxyPort(self, proxyPort, port):
        name = self.__in_proxy.proxyName(proxyPort)
        if name is None:
            return False

        return self.connectInputProxy(name, port)

    def connectOutputProxyPort(self, proxyPort, port):
        name = self.__out_proxy.proxyName(proxyPort)
        if name is None:
            return False

        return self.connectOutputProxy(name, port)

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

    def disconnectInputProxyPort(self, proxyPort, port):
        name = self.__in_proxy.proxyName(proxyPort)
        if name is None:
            return False

        return self.disconnectInputProxy(name, port)

    def disconnectOutputProxyPort(self, proxyPort, port):
        name = self.__out_proxy.proxyName(proxyPort)
        if name is None:
            return False

        return self.disconnectOutputProxy(name, port)

    def disconnectInputProxy(self, name, port):
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

        return self.__in_proxy.disconnect(name, port, is_inside)

    def disconnectOutputProxy(self, name, port):
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

        return self.__out_proxy.disconnect(name, port, is_inside)
