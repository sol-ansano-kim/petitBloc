import multiprocessing
import copy


class QueueManager(object):
    __Count = 0
    __Queues = []

    @staticmethod
    def Reset():
        for q in QueueManager.__Queues:
            q.close()
            del q

        QueueManager.__Queues = []
        QueueManager.__Count = 0

    @staticmethod
    def Count():
        return QueueManager.__Count

    @staticmethod
    def CreateQueue():
        QueueManager.__Count += 1
        q = multiprocessing.Queue()
        QueueManager.__Queues.append(q)

        return q

    @staticmethod
    def DeleteQueue(q):
        if q.empty():
            QueueManager.__Count -= 1
            QueueManager.__Queues.remove(q)
            q.close()
            del q
            return None

        return q


class ProcessWorker(multiprocessing.Process):
    def __init__(self, obj, args=(), kwargs={}):
        super(ProcessWorker, self).__init__(target=obj.run, args=args, kwargs=kwargs)
        self.daemon = True
        self.__obj = obj

    def start(self):
        self.__obj.activate()
        super(ProcessWorker, self).start()

    def terminate(self):
        if not self.__obj.isTerminated():
            self.__obj.terminate()

        super(ProcessWorker, self).terminate()


class ProcessManager(object):
    __Processes = []
    __MaxProcess = multiprocessing.cpu_count() - 1 or 1

    @staticmethod
    def SetMaxProcess(num):
        if num <= 0:
            ProcessManager.__MaxProcess = multiprocessing.cpu_count() - 1 or 1
        else:
            ProcessManager.__MaxProcess = num

    @staticmethod
    def Reset():
        for p in ProcessManager.__Processes:
            p.terminate()
            del p

        ProcessManager.__Processes = []
        ProcessManager.__MaxProcess = multiprocessing.cpu_count() - 1 or 1

    @staticmethod
    def Count():
        return len(ProcessManager.__Processes)

    @staticmethod
    def Submit(obj, args=(), kwargs={}):
        while (len(ProcessManager.__Processes) >= ProcessManager.__MaxProcess):
            for p in ProcessManager.__Processes:
                if p.is_alive():
                    continue
                else:
                    ProcessManager.DeleteProcess(p)

        p = ProcessWorker(obj, args=args, kwargs=kwargs)
        ProcessManager.__Processes.append(p)
        p.start()

    @staticmethod
    def DeleteProcess(p):
        p.terminate()
        ProcessManager.__Processes.remove(p)

    @staticmethod
    def Join():
        while (ProcessManager.__Processes):
            for p in ProcessManager.__Processes:
                if not p.is_alive():
                    ProcessManager.DeleteProcess(p)


def RunSchedule(schedule, maxProcess=0):
    QueueManager.Reset()
    ProcessManager.Reset()
    ProcessManager.SetMaxProcess(maxProcess)

    schedule = copy.copy(schedule)

    for s in schedule:
        s.resetState()

    while (schedule):
        next_bloc = None
        while (True):
            bloc = schedule.pop(0)
            if bloc.isTerminated() or bloc.isWorking():
                continue

            suspend = False

            for up in bloc.upstream():
                if up.isWaiting():
                    suspend = True
                    break

            if suspend:
                schedule.append(bloc)
                continue

            next_bloc = bloc
            break

        ProcessManager.Submit(next_bloc)

    ProcessManager.Join()

    QueueManager.Reset()
    ProcessManager.Reset()
