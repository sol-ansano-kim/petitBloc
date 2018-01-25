from . import processManager
from . import threadManager
from . import const


class WorkerManager(object):
    __UseProcess = False

    @staticmethod
    def SetUseProcess(value):
        if WorkerManager.__UseProcess != value:
            WorkerManager.ResetQueue()
            WorkerManager.ResetProcess()
            WorkerManager.ResetLog()

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
        if WorkerManager.UseProcess():
            processManager.LogManager.Debug(path, message)
        else:
            threadManager.LogManager.Debug(path, message)

    @staticmethod
    def Warn(path, message):
        if WorkerManager.UseProcess():
            processManager.LogManager.Warn(path, message)
        else:
            threadManager.LogManager.Warn(path, message)

    @staticmethod
    def Error(path, message):
        if WorkerManager.UseProcess():
            processManager.LogManager.Error(path, message)
        else:
            threadManager.LogManager.Error(path, message)

    @staticmethod
    def ErrorLogs():
        if WorkerManager.UseProcess():
            return processManager.LogManager.ErrorLogs()
        else:
            return threadManager.LogManager.ErrorLogs()

    @staticmethod
    def WarnLogs():
        if WorkerManager.UseProcess():
            return processManager.LogManager.WarnLogs()
        else:
            return threadManager.LogManager.WarnLogs()

    @staticmethod
    def DebugLogs():
        if WorkerManager.UseProcess():
            return processManager.LogManager.DebugLogs()
        else:
            return threadManager.LogManager.DebugLogs()

    @staticmethod
    def ErrorLog(path):
        if WorkerManager.UseProcess():
            return processManager.LogManager.ErrorLog(path)
        else:
            return threadManager.LogManager.ErrorLog(path)

    @staticmethod
    def WarnLog(path):
        if WorkerManager.UseProcess():
            return processManager.LogManager.WarnLog(path)
        else:
            return threadManager.LogManager.WarnLog(path)

    @staticmethod
    def DebugLog(path):
        if WorkerManager.UseProcess():
            return processManager.LogManager.DebugLog(path)
        else:
            return threadManager.LogManager.DebugLog(path)

    @staticmethod
    def ExecutionCount():
        if WorkerManager.UseProcess():
            return processManager.LogManager.ExecutionCount()
        else:
            return threadManager.LogManager.ExecutionCount()

    @staticmethod
    def TotalTime():
        if WorkerManager.UseProcess():
            return processManager.LogManager.TotalTime()
        else:
            return threadManager.LogManager.TotalTime()

    @staticmethod
    def Time(path):
        if WorkerManager.UseProcess():
            return processManager.LogManager.Time(path)
        else:
            return threadManager.LogManager.Time(path)

    @staticmethod
    def AverageTime():
        if WorkerManager.UseProcess():
            return processManager.LogManager.AverageTime()
        else:
            return threadManager.LogManager.AverageTime()

    @staticmethod
    def CreateQueue():
        if WorkerManager.UseProcess():
            return processManager.QueueManager.CreateQueue()
        else:
            return threadManager.QueueManager.CreateQueue()

    @staticmethod
    def DeleteQueue(q):
        if WorkerManager.UseProcess():
            processManager.QueueManager.DeleteQueue(q)
        else:
            threadManager.QueueManager.DeleteQueue(q)

    @staticmethod
    def RunSchedule(schedule, maxProcess=0, perProcessCallback=None):
        if WorkerManager.UseProcess():
            processManager.RunSchedule(schedule, maxProcess=maxProcess, perProcessCallback=perProcessCallback)
        else:
            threadManager.RunSchedule(schedule, maxProcess=maxProcess, perProcessCallback=perProcessCallback)

    @staticmethod
    def QueueCount():
        if WorkerManager.UseProcess():
            return processManager.QueueManager.Count()
        else:
            return threadManager.QueueManager.Count()

    @staticmethod
    def ResetLog():
        if WorkerManager.__UseProcess:
            processManager.LogManager.Reset()
        else:
            threadManager.LogManager.Reset()

    @staticmethod
    def ResetQueue():
        if WorkerManager.__UseProcess:
            processManager.QueueManager.Reset()
        else:
            threadManager.QueueManager.Reset()

    @staticmethod
    def ResetProcess():
        if WorkerManager.__UseProcess:
            processManager.ProcessManager.Reset()
        else:
            threadManager.ThreadManager.Reset()
