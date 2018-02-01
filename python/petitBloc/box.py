from . import chain
from . import component
from . import util
from . import core
from . import const
import copy
import re


ReSplitPath = re.compile("^[/](?P<name>[a-zA-Z0-9_]+)")


class SceneContext(component.Component):
    def __init__(self, name="", parent=None):
        super(SceneContext, self).__init__(name=self.__class__.__name__, parent=parent)

    def expandable(self):
        return True

    def getContext(self):
        context = {}
        for p in self.params():
            context[p.name()] = p.get()

        return context


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
        self.__context = None
        self.__blocks = []
        self.__in_proxy = ProxyBlock(ProxyBlock.In, name=const.InProxyBlock, parent=self)
        self.__out_proxy = ProxyBlock(ProxyBlock.Out, name=const.OutProxyBlock, parent=self)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Box<'{}'>".format(self.name())

    def ancestor(self):
        if self.parent() is None:
            return self

        return self.parent().ancestor()

    def hasNetwork(self):
        return True

    def expandable(self):
        return True

    def getSchedule(self):
        schedule = []
        initblocs = []
        blocs = []

        if self.__context is not None:
            schedule.append(self.__context)

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

    def block(self, name):
        for b in self.__blocks + [self.__in_proxy, self.__out_proxy]:
            if b.name() == name:
                return b

        return None

    def findBlock(self, blockPath):
        current_block = self
        blpt = blockPath

        while (current_block):
            if not isinstance(current_block, Box):
                break

            if current_block.path() == blockPath:
                break

            blpt = ReSplitPath.sub("", blpt)

            res = ReSplitPath.search(blpt)
            if not res:
                current_block = current_block.block(blpt)
            else:
                current_block = current_block.block(res.group("name"))

        if current_block is None or current_block.path() != blockPath:
            return None

        return current_block

    def blockCount(self):
        return len(self.__blocks)

    def getUniqueName(self, bloc, name):
        if not name or not util.ValidateName(name):
            name = bloc.__class__.__name__

        all_names = [const.InProxyBlock, const.OutProxyBlock] + map(lambda x: x.name(), filter(lambda y: y != bloc, self.__blocks))

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

    def createContext(self):
        if self.ancestor() != self:
            return None

        if self.__context is not None:
            return None

        self.__context = SceneContext()
        self.__context.setParent(self)

        return self.__context

    def deleteContext(self):
        self.__context = None

    def getContext(self):
        if self.__context is None:
            return {}

        return self.__context.getContext()

    def addContext(self, typeClass, name=None):
        if self.__context is None:
            return None

        return self.__context.addParam(typeClass, name=name)

    def removeContext(self, name_or_param):
        if self.__context is None:
            return False

        return self.__context.removeParam(name_or_param)

    def context(self, name):
        if self.__context is None:
            return None

        return self.__context.param(name)

    def contexts(self):
        if self.__context is None:
            for p in []:
                yield p
        else:
            for p in self.__context.params():
                yield p

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
