from . import processManager
from . import threadManager
from . import const


class WorkerManager(object):
    __UseProcess = False
    __LogManager = threadManager.LogManager
    __QueueManager = threadManager.QueueManager
    __ProcessManager = threadManager.ThreadManager
    __Module = threadManager

    @staticmethod
    def SetUseProcess(value):
        if WorkerManager.__UseProcess != value:
            WorkerManager.ResetQueue()
            WorkerManager.ResetProcess()
            WorkerManager.ResetLog()
            if not value:
                WorkerManager.__LogManager = threadManager.LogManager
                WorkerManager.__QueueManager = threadManager.QueueManager
                WorkerManager.__ProcessManager = threadManager.ThreadManager
                WorkerManager.__Module = threadManager
            else:
                WorkerManager.__LogManager = processManager.LogManager
                WorkerManager.__QueueManager = processManager.QueueManager
                WorkerManager.__ProcessManager = processManager.ProcessManager
                WorkerManager.__Module = processManager

        WorkerManager.__UseProcess = value

    @staticmethod
    def UseProcess():
        return WorkerManager.__UseProcess

    @staticmethod
    def SetLogLevel(l):
        if not isinstance(l, const.LogLevel):
            print("Warning : Invalid Log level")
            return False

        processManager.LogManager.SetLogLevel(l)
        threadManager.LogManager.SetLogLevel(l)

        return True

    @staticmethod
    def Debug(path, message):
        WorkerManager.__LogManager.Debug(path, message)

    @staticmethod
    def Warn(path, message):
        WorkerManager.__LogManager.Warn(path, message)

    @staticmethod
    def Error(path, message):
        WorkerManager.__LogManager.Error(path, message)

    @staticmethod
    def ErrorLogs():
        return WorkerManager.__LogManager.ErrorLogs()

    @staticmethod
    def WarnLogs():
        return WorkerManager.__LogManager.WarnLogs()

    @staticmethod
    def DebugLogs():
        return WorkerManager.__LogManager.DebugLogs()

    @staticmethod
    def ErrorLog(path):
        return WorkerManager.__LogManager.ErrorLog(path)

    @staticmethod
    def WarnLog(path):
        return WorkerManager.__LogManager.WarnLog(path)

    @staticmethod
    def DebugLog(path):
        return WorkerManager.__LogManager.DebugLog(path)

    @staticmethod
    def ExecutionCount():
        return WorkerManager.__LogManager.ExecutionCount()

    @staticmethod
    def TotalTime():
        return WorkerManager.__LogManager.TotalTime()

    @staticmethod
    def TimeLogs():
        return WorkerManager.__LogManager.TimeLogs()

    @staticmethod
    def TimeLog(path):
        return WorkerManager.__LogManager.TimeLog(path)

    @staticmethod
    def AverageTime():
        return WorkerManager.__LogManager.AverageTime()

    @staticmethod
    def CreateQueue():
        return WorkerManager.__QueueManager.CreateQueue()

    @staticmethod
    def DeleteQueue(q):
        WorkerManager.__QueueManager.DeleteQueue(q)

    @staticmethod
    def RunSchedule(schedule, maxProcess=0, perProcessCallback=None):
        WorkerManager.__Module.RunSchedule(schedule, maxProcess=maxProcess, perProcessCallback=perProcessCallback)

    @staticmethod
    def QueueCount():
        return WorkerManager.__QueueManager.Count()

    @staticmethod
    def ResetLog():
        WorkerManager.__LogManager.Reset()

    @staticmethod
    def ResetQueue():
        WorkerManager.__QueueManager.Reset()

    @staticmethod
    def ResetProcess():
        WorkerManager.__ProcessManager.Reset()
