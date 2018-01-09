from . import chain
from . import block
import multiprocessing


class Box(block.Component):
    def __init__(self, name="", parent=None):
        super(Box, self).__init__(name="", parent=parent)
        self.__blocks = []
        self.__chains = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Box<'{}'>".format(self.name())

    def __correctDownStreams(self, bloc):
        result = []
        for db in bloc.downstream():
            result.append(db)
            result += self.__correctDownStreams(db)

        return result

    def run(self):
        # TODO : improve process queue
        # TODO : support subnet
        max_process = multiprocessing.cpu_count() - 1 or 1
        schedule = []
        initblocs = []
        blocs = []

        for bloc in self.__blocks:
            ups = bloc.upstream()

            if filter(lambda x: not isinstance(x, Box), ups):
                blocs.append(bloc)
                continue

            schedule.append(bloc)
            initblocs.append(bloc)

        for intbloc in initblocs:
            for db in self.__correctDownStreams(intbloc):
                if db in blocs:
                    blocs.remove(db)
                schedule.append(db)

        for bloc in blocs:
            schedule.append(bloc)

        processes = []

        for x in self.__blocks:
            multiprocessing.Process(target=x.run)

        while (schedule):
            alives = []

            for p in processes:
                if p.is_alive():
                    alives.append(p)

            if len(alives) >= max_process:
                continue

            next_bloc = None
            while (True):
                bloc = schedule.pop(0)
                if bloc.isTerminated() or bloc.isWorking():
                    continue

                suspend = False

                for up in bloc.upstream():
                    if isinstance(up, Box):
                        continue

                    if up.isWaiting():
                        suspend = True
                        break

                if suspend:
                    schedule.append(bloc)
                    continue

                next_bloc = bloc
                break

            next_bloc.activate()
            p = multiprocessing.Process(target=next_bloc.run)
            p.daemon = True
            p.start()
            alives.append(p)
            processes = alives

        for p in processes:
            p.join()

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
