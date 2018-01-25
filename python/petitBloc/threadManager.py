import threading
import Queue
import copy
import time
from . import const


class LogManager(object):
    __LogLevel = const.LogLevel.Error

    __Count = 0
    __TotalTime = 0
    __TimeLog = {}
    __ErrorLog = {}
    __WarnLog = {}
    __DebugLog = {}

    @staticmethod
    def SetLogLevel(l):
        LogManager.__LogLevel = l

    @staticmethod
    def Reset():
        LogManager.__Count = 0
        LogManager.__TotalTime = 0
        LogManager.__TimeLog = {}
        LogManager.__ErrorLog = {}
        LogManager.__WarnLog = {}
        LogManager.__DebugLog = {}

    @staticmethod
    def IncreaseCount():
        LogManager.__Count += 1

    @staticmethod
    def TimeReport(path, v):
        LogManager.__TotalTime += v
        LogManager.__TimeLog[path] = v

    @staticmethod
    def ExecutionCount():
        return LogManager.__Count

    @staticmethod
    def TotalTime():
        return LogManager.__TotalTime

    @staticmethod
    def TimeLog(path):
        return LogManager.__TimeLog.get(path, -1)

    @staticmethod
    def TimeLogs():
        return copy.copy(LogManager.__TimeLog)

    @staticmethod
    def AverageTime():
        if LogManager.__Count == 0:
            return 0

        return LogManager.__TotalTime / float(LogManager.__Count)

    @staticmethod
    def ErrorLogs():
        return copy.deepcopy(LogManager.__ErrorLog)

    @staticmethod
    def WarnLogs():
        return copy.deepcopy(LogManager.__WarnLog)

    @staticmethod
    def DebugLogs():
        return copy.deepcopy(LogManager.__DebugLog)

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
        if LogManager.__LogLevel <= const.LogLevel.Error:
            print("Error : {}".format(message))

        log_list = LogManager.__ErrorLog.get(path, [])
        log_list.append(message)
        LogManager.__ErrorLog[path] = log_list

    @staticmethod
    def Warn(path, message):
        if LogManager.__LogLevel <= const.LogLevel.Warn:
            print("Warning : {}".format(message))

        log_list = LogManager.__WarnLog.get(path, [])
        log_list.append(message)
        LogManager.__WarnLog[path] = log_list

    @staticmethod
    def Debug(path, message):
        if LogManager.__LogLevel <= const.LogLevel.Debug:
            print("Debug : {}".format(message))

        log_list = LogManager.__DebugLog.get(path, [])
        log_list.append(message)
        LogManager.__DebugLog[path] = log_list


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

    def run(self):
        LogManager.IncreaseCount()
        st = time.time()

        try:
            self.__obj.run()
        except Exception as e:
            self.__success = False
            LogManager.Error(self.__obj.path(), e)

        LogManager.TimeReport(self.__obj.path(), time.time() - st)

    def start(self):
        self.__obj.activate()
        super(ProcessWorker, self).start()

    def terminate(self):
        if not self.__obj.isTerminated():
            self.__obj.terminate(self.__success)

class ThreadManager(object):
    __Threads = []
    __MaxThreads = 999
    __PerProcessCallback = None

    @staticmethod
    def SetPerProcessCallback(callback):
        ThreadManager.__PerProcessCallback = callback

    @staticmethod
    def RunPerProcessCallback():
        if ThreadManager.__PerProcessCallback is not None:
            ThreadManager.__PerProcessCallback()

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
        ThreadManager.__PerProcessCallback = None

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
                    ThreadManager.RunPerProcessCallback()
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
                    ThreadManager.RunPerProcessCallback()
                    ThreadManager.DeleteProcess(p)


def RunSchedule(schedule, maxProcess=0, perProcessCallback=None):
    LogManager.Reset()
    QueueManager.Reset()
    ThreadManager.Reset()
    ThreadManager.SetMaxProcess(maxProcess)
    ThreadManager.SetPerProcessCallback(perProcessCallback)

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

        ThreadManager.Submit(next_bloc)

    ThreadManager.Join()

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

    QueueManager.Reset()
    ThreadManager.Reset()
