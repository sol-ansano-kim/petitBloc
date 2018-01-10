from . import chain
from . import block
from . import component


class Box(component.Component):
    def __init__(self, name="", parent=None):
        super(Box, self).__init__(name="", parent=parent)
        self.__blocks = []
        self.__chains = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Box<'{}'>".format(self.name())

    def hasSubnet(self):
        return True

    def __correctDownStreams(self, bloc):
        result = []

        cur_blocs = [bloc]
        while (cur_blocs):
            dns = []
            for b in cur_blocs:
                result += b.getSchedule()
                dns += filter(lambda x : x != self, b.downstream())

            cur_blocs = dns

        return result

    def getSchedule(self):
        schedule = []
        initblocs = []
        blocs = []
        boxies = []

        for bloc in self.__blocks:
            if filter(lambda x : x != self, bloc.upstream()):
                blocs.append(bloc)
                continue

            initblocs.append(bloc)

        for intbloc in initblocs:
            for db in self.__correctDownStreams(intbloc):
                if db in blocs:
                    blocs.remove(db)
                schedule.append(db)

        for bloc in blocs:
            schedule.append(bloc)

        return schedule

    def run(self):
        pass

    def initialize(self):
        pass

    def blocks(self):
        for b in self.__blocks:
            yield b

    def blockCount(self):
        return len(self.__blocks)

    def addBlock(self, block):
        if block in self.__blocks:
            return False

        self.__blocks.append(block)
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
