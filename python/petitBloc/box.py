from . import chain
from . import block
from . import component
from . import util
from . import core


class Box(component.Component):
    def __init__(self, name="", parent=None):
        super(Box, self).__init__(name=name, parent=parent)
        self.__blocks = []
        self.__chains = []
        self.__proxy_params = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Box<'{}'>".format(self.name())

    def getSchedule(self):
        schedule = []
        initblocs = []
        blocs = []

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

        if dstPort.isConnected():
            c = dstPort.getChains()[0]
            if c in self.__chains:
                self.__chains.remove(c)

        c = chain.Chain(srcPort, dstPort)
        if c is None:
            return False

        self.__chains.append(c)

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
