import multiprocessing
import copy


class ValueManager(object):
    __Count = 0
    __Values = []

    @staticmethod
    def Reset():
        for v in ValueManager.__Values:
            del v

    @staticmethod
    def Count():
        return ValueManager.__Count

    @staticmethod
    def CreateValue(valueType, defaultValue=None):
        ValueManager.__Count += 1

        if defaultValue is not None:
            v = multiprocessing.Value(valueType, defaultValue)
        else:
            v = multiprocessing.Value(valueType)

        ValueManager.__Values.append(v)

        return v

    @staticmethod
    def DeleteValue(v):
        ValueManager.__Count -= 1
        ValueManager.__Values.remove(v)
        del v


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
        QueueManager.__Count -= 1
        QueueManager.__Queues.remove(q)
        q.close()
        del q


class ProcessWorker(multiprocessing.Process):
    def __init__(self, obj, args=(), kwargs={}):
        super(ProcessWorker, self).__init__()
        self.daemon = True
        self.__obj = obj
        self.__has_error = ValueManager.CreateValue("i", 0)

    def run(self):
        try:
            self.__obj.run()
        except Exception as e:
            self.__has_error.value = 1

    def start(self):
        self.__obj.activate()
        super(ProcessWorker, self).start()

    def terminate(self):
        if not self.__obj.isTerminated():
            self.__obj.terminate(self.__has_error.value == 0)

        ValueManager.DeleteValue(self.__has_error)

        super(ProcessWorker, self).terminate()


class ProcessManager(object):
    __Processes = []
    __MaxProcess = multiprocessing.cpu_count() - 1 or 1
    __PerProcessCallback = None

    @staticmethod
    def SetPerProcessCallback(callback):
        ProcessManager.__PerProcessCallback = callback

    @staticmethod
    def RunPerProcessCallback():
        if ProcessManager.__PerProcessCallback is not None:
            ProcessManager.__PerProcessCallback()

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
        ProcessManager.__PerProcessCallback = None

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
                    ProcessManager.RunPerProcessCallback()
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
                    ProcessManager.RunPerProcessCallback()
                    ProcessManager.DeleteProcess(p)


def RunSchedule(schedule, maxProcess=0, perProcessCallback=None):
    ValueManager.Reset()
    QueueManager.Reset()
    ProcessManager.Reset()
    ProcessManager.SetMaxProcess(maxProcess)
    ProcessManager.SetPerProcessCallback(perProcessCallback)

    work_schedule = copy.copy(schedule)

    for s in work_schedule:
        s.resetState()

    while (work_schedule):
        next_bloc = None
        while (True):
            bloc = work_schedule.pop(0)
            if bloc.isTerminated() or bloc.isWorking() or bloc.isFailed():
                continue

            suspend = False

            for up in bloc.upstream():
                if up.isWaiting():
                    suspend = True
                    break

            if suspend:
                work_schedule.append(bloc)
                continue

            next_bloc = bloc
            break

        ProcessManager.Submit(next_bloc)

    ProcessManager.Join()

    for s in schedule:
        if not s.hasNetwork():
            continue

        success = True
        for ss in s.getSchedule():
            if ss.isFailed():
                success = False
                break

        s.terminate(success)

    if perProcessCallback is not None:
        perProcessCallback()

    ValueManager.Reset()
    QueueManager.Reset()
    ProcessManager.Reset()
