import threading
import Queue
import copy
import time
from . import const
import subprocess
import multiprocessing


class SubprocessWorker(object):
    def __init__(self, cmd):
        self.__command = cmd
        self.__p = subprocess.Popen(cmd, shell=True)

    def command(self):
        return self.__command

    def isRunning(self):
        return self.__p.poll() is None

    def result(self):
        res = self.__p.wait() == 0
        SubprocessManager.DeleteProcess(self)

        return res


class SubprocessManager(object):
    __Processes = []
    __MaxProcess = multiprocessing.cpu_count() - 1 or 1
    __WaitTime = 0.5
    __Lock = threading.Lock()

    @staticmethod
    def SetMaxProcess(num):
        if num <= 0:
            SubprocessManager.__MaxProcess = multiprocessing.cpu_count() - 1 or 1
        else:
            SubprocessManager.__MaxProcess = num

    @staticmethod
    def Reset():
        for p in SubprocessManager.__Processes:
            del p

        SubprocessManager.__Processes = []
        SubprocessManager.__MaxProcess = multiprocessing.cpu_count() - 1 or 1

    @staticmethod
    def Count():
        return len(SubprocessManager.__Processes)

    @staticmethod
    def DeleteProcess(p):
        SubprocessManager.__Lock.acquire()

        if p in SubprocessManager.__Processes:
            SubprocessManager.__Processes.remove(p)

        SubprocessManager.__Lock.release()

    @staticmethod
    def Submit(cmd):
        while (True):
            SubprocessManager.__Lock.acquire()

            if SubprocessManager.Count() < SubprocessManager.__MaxProcess:
                worker = SubprocessWorker(cmd)
                SubprocessManager.__Processes.append(worker)
                SubprocessManager.__Lock.release()

                return worker

            SubprocessManager.__Lock.release()

            for p in SubprocessManager.__Processes:
                if not p.isRunning():
                    SubprocessManager.DeleteProcess(p)

            time.sleep(SubprocessManager.__WaitTime)


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
    class __Value(object):
        def __init__(self, valueType, defaultValue=None):
            self.__value_type = valueType
            self.__value = defaultValue

        @property
        def value(self):
            return self.__value

        @value.setter
        def value(self, v):
            self.__value = v

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

        v = ValueManager.__Value(valueType, defaultValue=defaultValue)
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
        if q in QueueManager.__Queues:
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
        if not self.__obj.isOver():
            self.__obj.terminate(self.__success)

class ThreadManager(object):
    __Threads = []
    __MaxThreads = 999
    __PerProcessCallback = None
    __Lock = threading.Lock()

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
            ThreadManager.LockAcquire()
            ThreadManager.CleaunUp()
            ThreadManager.LockRelease()

        p = ProcessWorker(obj, args=args, kwargs=kwargs)
        ThreadManager.__Threads.append(p)
        p.start()

    @staticmethod
    def CleaunUp():
        for p in ThreadManager.__Threads:
            if not p.is_alive():
                ThreadManager.RunPerProcessCallback()
                ThreadManager.DeleteProcess(p)

    @staticmethod
    def IsWorking():
        working = False

        ThreadManager.CleaunUp()

        for p in ThreadManager.__Threads:
            if p.is_alive():
                working = True
                break

        return working

    @staticmethod
    def LockAcquire():
        ThreadManager.__Lock.acquire()

    @staticmethod
    def LockRelase():
        ThreadManager.__Lock.release()

    @staticmethod
    def DeleteProcess(p):
        p.terminate()
        if p in ThreadManager.__Threads:
            ThreadManager.__Threads.remove(p)

    @staticmethod
    def Join():
        while (ThreadManager.__Threads):
            for p in ThreadManager.__Threads:
                if not p.is_alive():
                    ThreadManager.RunPerProcessCallback()
                    ThreadManager.DeleteProcess(p)


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
    ThreadManager.Reset()
    LogManager.Reset()
    QueueManager.Reset()
    ValueManager.Reset()
    SubprocessManager.Reset()
    ThreadManager.SetMaxProcess(maxProcess)
    ThreadManager.SetPerProcessCallback(perProcessCallback)

    work_schedule = copy.copy(schedule)

    for s in work_schedule:
        s.resetState()

    while (work_schedule):
        ThreadManager.CleaunUp()

        bloc = work_schedule.pop(0)
        if bloc.isTerminated() or bloc.isWorking() or bloc.isFailed() or bloc.isByPassing():
            continue

        ThreadManager.LockAcquire()

        if __needToWait(bloc):
            work_schedule.append(bloc)
            ThreadManager.LockRelase()
            continue

        ThreadManager.LockRelase()
        ThreadManager.Submit(bloc)

    ThreadManager.Join()

    for s in work_schedule:
        s.clear()

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
    ValueManager.Reset()
    ThreadManager.Reset()
    SubprocessManager.Reset()
