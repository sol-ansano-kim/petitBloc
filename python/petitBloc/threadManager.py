import threading
import Queue
import copy


class QueueManager(object):
    __Count = 0
    __Queues = []

    @staticmethod
    def Reset():
        for q in QueueManager.__Queues:
            del q

        QueueManager.__Queues = []
        QueueManager.__Count = 0

    @staticmethod
    def Count():
        return QueueManager.__Count

    @staticmethod
    def CreateQueue():
        QueueManager.__Count += 1
        q = Queue.Queue()
        QueueManager.__Queues.append(q)

        return q

    @staticmethod
    def DeleteQueue(q):
        QueueManager.__Count -= 1
        QueueManager.__Queues.remove(q)
        del q


class ProcessWorker(threading.Thread):
    def __init__(self, obj, args=(), kwargs={}):
        super(ProcessWorker, self).__init__()
        self.daemon = True
        self.__obj = obj
        self.__args = args
        self.__kwargs = kwargs
        self.__success = True
        self.__error_log = ""

    def run(self):
        try:
            self.__obj.run()
        except Exception as e:
            self.__success = False
            self.__error_log = e

    def start(self):
        self.__obj.activate()
        super(ProcessWorker, self).start()

    def terminate(self):
        if not self.__obj.isTerminated():
            self.__obj.terminate(self.__success)

class ThreadManager(object):
    __Threads = []
    __MaxThreads = 999

    @staticmethod
    def SetMaxProcess(num):
        if num <= 0:
            ThreadManager.__MaxThreads = 999
        else:
            ThreadManager.__MaxThreads = num

    @staticmethod
    def Reset():
        for p in ThreadManager.__Threads:
            p.terminate()
            del p

        ThreadManager.__Threads = []
        ThreadManager.__MaxThreads = 999

    @staticmethod
    def Count():
        return len(ThreadManager.__Threads)

    @staticmethod
    def Submit(obj, args=(), kwargs={}):
        while (len(ThreadManager.__Threads) >= ThreadManager.__MaxThreads):
            for p in ThreadManager.__Threads:
                if p.is_alive():
                    continue
                else:
                    ThreadManager.DeleteProcess(p)

        p = ProcessWorker(obj, args=args, kwargs=kwargs)
        ThreadManager.__Threads.append(p)
        p.start()

    @staticmethod
    def DeleteProcess(p):
        p.terminate()
        ThreadManager.__Threads.remove(p)

    @staticmethod
    def Join():
        while (ThreadManager.__Threads):
            for p in ThreadManager.__Threads:
                if not p.is_alive():
                    ThreadManager.DeleteProcess(p)


def RunSchedule(schedule, maxProcess=0):
    QueueManager.Reset()
    ThreadManager.Reset()
    ThreadManager.SetMaxProcess(maxProcess)

    schedule = copy.copy(schedule)

    for s in schedule:
        s.resetState()

    while (schedule):
        next_bloc = None
        while (True):
            bloc = schedule.pop(0)
            if bloc.isTerminated() or bloc.isWorking() or bloc.isFailed():
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

        ThreadManager.Submit(next_bloc)

    ThreadManager.Join()

    QueueManager.Reset()
    ThreadManager.Reset()
