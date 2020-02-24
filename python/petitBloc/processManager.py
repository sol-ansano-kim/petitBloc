import time
import copy
import multiprocessing
from . import const
from . import subproc


class SubprocessManager(object):
    __Manager = None
    __Processes = None
    __MaxProcess = multiprocessing.cpu_count() - 1 or 1
    __WaitTime = 0.5
    __Lock = multiprocessing.Lock()

    @staticmethod
    def Initialize():
        if SubprocessManager.__Manager is None:
            SubprocessManager.__Manager = multiprocessing.Manager()
            SubprocessManager.__Processes = SubprocessManager.__Manager.dict()

    @staticmethod
    def SetMaxProcess(num):
        if num <= 0:
            SubprocessManager.__MaxProcess = multiprocessing.cpu_count() - 1 or 1
        else:
            SubprocessManager.__MaxProcess = num

    @staticmethod
    def Reset():
        if SubprocessManager.__Manager is not None:
            for k, p in SubprocessManager.__Processes.items():
                del p

            SubprocessManager.__Processes.clear()

        SubprocessManager.__MaxProcess = multiprocessing.cpu_count() - 1 or 1

    @staticmethod
    def Count():
        return len(SubprocessManager.__Processes)

    @staticmethod
    def Submit(cmd):
        index = 0
        while (True):
            SubprocessManager.__Lock.acquire()
            running_count = 0

            for index, p in SubprocessManager.__Processes.items():
                if p.isRunning():
                    running_count += 1

            if running_count < SubprocessManager.__MaxProcess:
                worker = subproc.SubprocessWorker(cmd)
                SubprocessManager.__Processes[index] = worker

                index += 1

                SubprocessManager.__Lock.release()

                return worker

            SubprocessManager.__Lock.release()

            time.sleep(SubprocessManager.__WaitTime)


class LogManager(object):
    __LogLevel = const.LogLevel.Error

    __Manager = None
    __Count = None
    __TotalTime = None
    __TimeLog = None
    __ErrorLog = None
    __WarnLog = None
    __DebugLog = None

    @staticmethod
    def SetLogLevel(l):
        LogManager.__LogLevel = l

    @staticmethod
    def Initialize():
        if LogManager.__Manager is None:
            LogManager.__Manager = multiprocessing.Manager()
            LogManager.__Count = multiprocessing.Value("i", 0)
            LogManager.__TotalTime = multiprocessing.Value("f", 0.0)
            LogManager.__TimeLog = LogManager.__Manager.dict()
            LogManager.__ErrorLog = LogManager.__Manager.dict()
            LogManager.__WarnLog = LogManager.__Manager.dict()
            LogManager.__DebugLog = LogManager.__Manager.dict()

    @staticmethod
    def Reset():
        if LogManager.__Manager is not None:
            LogManager.__Count.value = 0
            LogManager.__TotalTime.value = 0.0
            LogManager.__TimeLog.clear()
            LogManager.__ErrorLog.clear()
            LogManager.__WarnLog.clear()
            LogManager.__DebugLog.clear()

    @staticmethod
    def IncreaseCount():
        LogManager.__Count.value += 1

    @staticmethod
    def TimeReport(path, v):
        LogManager.__TotalTime.value += v
        LogManager.__TimeLog[path] = v

    @staticmethod
    def ExecutionCount():
        return LogManager.__Count.value

    @staticmethod
    def TotalTime():
        return LogManager.__TotalTime.value

    @staticmethod
    def TimeLog(path):
        return LogManager.__TimeLog.get(path, -1)

    @staticmethod
    def AverageTime():
        if LogManager.__Count.value == 0:
            return 0

        return LogManager.__TotalTime.value / float(LogManager.__Count.value)

    @staticmethod
    def TimeLogs():
        return LogManager.__TimeLog.copy()

    @staticmethod
    def ErrorLogs():
        return LogManager.__ErrorLog.copy()

    @staticmethod
    def WarnLogs():
        return LogManager.__WarnLog.copy()

    @staticmethod
    def DebugLogs():
        return LogManager.__DebugLog.copy()

    @staticmethod
    def ErrorLog(path):
        return copy.copy(LogManager.__ErrorLog.get(path, []))

    @staticmethod
    def WarnLog(path):
        return copy.copy(LogManager.__WarnLog.get(path, []))

    @staticmethod
    def DebugLog(path):
        return copy.copy(LogManager.__DebugLog.get(path, []))

    @staticmethod
    def Error(path, message):
        if LogManager.__LogLevel >= const.LogLevel.Error:
            print("Error : {}".format(message))

        log_list = LogManager.__ErrorLog.get(path, [])
        log_list.append(str(message))
        LogManager.__ErrorLog[path] = log_list

    @staticmethod
    def Warn(path, message):
        if LogManager.__LogLevel >= const.LogLevel.Warn:
            print("Warning : {}".format(message))

        log_list = LogManager.__WarnLog.get(path, [])
        log_list.append(str(message))
        LogManager.__WarnLog[path] = log_list

    @staticmethod
    def Debug(path, message):
        if LogManager.__LogLevel >= const.LogLevel.Debug:
            print("Debug : {}".format(message))

        log_list = LogManager.__DebugLog.get(path, [])
        log_list.append(str(message))
        LogManager.__DebugLog[path] = log_list


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
        if v in ValueManager.__Values:
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
        if q in QueueManager.__Queues:
            QueueManager.__Count -= 1
            QueueManager.__Queues.remove(q)
        q.close()
        del q


class ProcessWorker(multiprocessing.Process):
    def __init__(self, obj, *args, **kwargs):
        super(ProcessWorker, self).__init__()
        self.daemon = True
        self.__obj = obj
        self.__has_error = ValueManager.CreateValue("i", 0)

    def run(self):
        LogManager.IncreaseCount()
        st = time.time()

        try:
            self.__obj.run()
        except Exception as e:
            self.__has_error.value = 1
            LogManager.Error(self.__obj.path(), e)

        res = self.__obj.output(const.BlockResultPortName)
        if res:
            res.send(self.__has_error.value == 0)

        LogManager.TimeReport(self.__obj.path(), time.time() - st)

    def start(self):
        self.__obj.activate()
        super(ProcessWorker, self).start()

    def obj(self):
        return self.__obj

    def terminate(self):
        if not self.__obj.isOver():
            self.__obj.terminate(self.__has_error.value == 0)

        ValueManager.DeleteValue(self.__has_error)

        super(ProcessWorker, self).terminate()


class ProcessManager(object):
    __Processes = []
    __MaxProcess = multiprocessing.cpu_count() - 1 or 1
    __PerProcessCallback = None
    __Lock = multiprocessing.Lock()

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
    def Submit(obj, *args, **kwargs):
        while (len(ProcessManager.__Processes) >= ProcessManager.__MaxProcess):
            ProcessManager.CleanUp()

        LogManager.Debug("__main__", "  {0:>10}      {1}".format("Start -", obj.path()))
        p = ProcessWorker(obj, *args, **kwargs)
        ProcessManager.__Processes.append(p)

        p.start()

    @staticmethod
    def CleanUp():
        for p in ProcessManager.__Processes:
            if not p.is_alive():
                ProcessManager.RunPerProcessCallback()
                ProcessManager.DeleteProcess(p)

    @staticmethod
    def IsWorking():
        ProcessManager.CleanUp()

        working = False
        for p in ProcessManager.__Processes:
            if p.is_alive():
                working = True
                break

        return working

    @staticmethod
    def LockAcquire():
        ProcessManager.__Lock.acquire()

    @staticmethod
    def LockRelease():
        ProcessManager.__Lock.release()

    @staticmethod
    def DeleteProcess(p):
        p.terminate()
        LogManager.Debug("__main__", "  {0:>10}      {1}".format("End -", p.obj().path()))

        if p in ProcessManager.__Processes:
            ProcessManager.__Processes.remove(p)

    @staticmethod
    def Join():
        while (ProcessManager.__Processes):
            for p in ProcessManager.__Processes:
                if not p.is_alive():
                    ProcessManager.RunPerProcessCallback()
                    ProcessManager.DeleteProcess(p)


def __needToWait(bloc):
    suspend = __parentSuspended(bloc)

    if not suspend:
        for up in bloc.upstream(ignoreProxy=False):
            if not up.isByPassing() and up.isWaiting():
                suspend = True
                break

    return suspend


def __parentSuspended(bloc):
    parent = bloc.parent()
    if parent and parent.isWaiting():
        return True

    return False


def RunSchedule(schedule, maxProcess=0, perProcessCallback=None):
    LogManager.Initialize()
    LogManager.Reset()
    st = time.time()

    LogManager.Debug("__main__", "## PetitBloc Start")

    SubprocessManager.Initialize()
    SubprocessManager.Reset()
    ProcessManager.Reset()
    ValueManager.Reset()
    QueueManager.Reset()
    ProcessManager.SetMaxProcess(maxProcess)
    ProcessManager.SetPerProcessCallback(perProcessCallback)

    need_to_terminate = []
    work_schedule = copy.copy(schedule)

    t1 = time.time()
    for s in work_schedule:
        s.resetState()

    while (work_schedule):
        ProcessManager.CleanUp()

        bloc = work_schedule.pop(0)
        if bloc.isTerminated() or bloc.isWorking() or bloc.isFailed():
            continue

        if bloc.isByPassing():
            res = bloc.output(const.BlockResultPortName)
            if res:
                res.activate()
                res.send(False)
                need_to_terminate.append(res)

            continue

        ProcessManager.LockAcquire()

        if __needToWait(bloc):
            LogManager.Debug("__main__", "  {0:>10}      {1}".format("Suspend -", bloc.path()))
            work_schedule.append(bloc)
            ProcessManager.LockRelease()
            continue

        ProcessManager.LockRelease()
        ProcessManager.Submit(bloc)

    ProcessManager.Join()
    t2 = time.time()

    # TODO : sometime pipe would be broken
    # do it more smarter..
    time.sleep(0.01)

    for s in schedule:
        if not s.hasNetwork():
            continue

        success = True
        for ss in s.getSchedule():
            if ss.isFailed():
                success = False
                break

        s.terminate(success)

    for p in need_to_terminate:
        p.terminate()

    if perProcessCallback is not None:
        perProcessCallback()

    ValueManager.Reset()
    QueueManager.Reset()
    ProcessManager.Reset()
    SubprocessManager.Reset()
    t3 = time.time()

    LogManager.Debug("__main__", "## PetitBloc End")
    LogManager.Debug("__main__", "Time log")
    LogManager.Debug("__main__", '  {0:<12} {1:>10}'.format("Initializing", round(t1 - st, 5)))
    LogManager.Debug("__main__", '  {0:<12} {1:>10}'.format("Computing", round(t2 - t1, 5)))
    LogManager.Debug("__main__", '  {0:<12} {1:>10}'.format("Finalizing", round(t3 - t2, 5)))
    LogManager.Debug("__main__", "Execution")
    LogManager.Debug("__main__", "  Run : {}".format(LogManager.ExecutionCount()))
    LogManager.Debug("__main__", "  Warning : {}".format(len(LogManager.WarnLogs().keys())))

    err_cnt = len(LogManager.ErrorLogs().keys())
    LogManager.Debug("__main__", "  Error : {}".format(err_cnt))

    return err_cnt == 0
