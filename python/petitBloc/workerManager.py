from . import processManager
from . import threadManager
from . import const


class WorkerManager(object):
    __UseProcess = False
    __LogManager = threadManager.LogManager
    __QueueManager = threadManager.QueueManager
    __ProcessManager = threadManager.ThreadManager
    __SubProcessManager = threadManager.SubprocessManager
    __ValueManager = threadManager.ValueManager
    __Module = threadManager

    @staticmethod
    def SetUseProcess(value):
        if WorkerManager.__UseProcess != value:
            WorkerManager.ResetQueue()
            WorkerManager.ResetProcess()
            WorkerManager.ResetLog()
            WorkerManager.ResetSubProcess()
            WorkerManager.ResetValues()

            if not value:
                WorkerManager.__LogManager = threadManager.LogManager
                WorkerManager.__QueueManager = threadManager.QueueManager
                WorkerManager.__ProcessManager = threadManager.ThreadManager
                WorkerManager.__SubProcessManager = threadManager.SubprocessManager
                WorkerManager.__ValueManager = threadManager.ValueManager
                WorkerManager.__Module = threadManager
            else:
                WorkerManager.__LogManager = processManager.LogManager
                WorkerManager.__QueueManager = processManager.QueueManager
                WorkerManager.__ProcessManager = processManager.ProcessManager
                WorkerManager.__SubProcessManager = processManager.SubprocessManager
                WorkerManager.__ValueManager = processManager.ValueManager
                WorkerManager.__Module = processManager

        WorkerManager.__UseProcess = value

    @staticmethod
    def UseProcess():
        return WorkerManager.__UseProcess

    @staticmethod
    def SetLogLevel(l):
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
    def CreateValue(valueType, defaultValue=None):
        return WorkerManager.__ValueManager.CreateValue(valueType, defaultValue)

    @staticmethod
    def DeleteValue(v):
        WorkerManager.__ValueManager.DeleteValue(v)

    @staticmethod
    def RunSchedule(schedule, maxProcess=0, perProcessCallback=None):
        return WorkerManager.__Module.RunSchedule(schedule, maxProcess=maxProcess, perProcessCallback=perProcessCallback)

    @staticmethod
    def ValueCount():
        return WorkerManager.__ValueManager.Count()

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

    @staticmethod
    def ResetSubProcess():
        WorkerManager.__SubProcessManager.Reset()

    @staticmethod
    def ResetValues():
        WorkerManager.__ValueManager.Reset()

    @staticmethod
    def SubmitSubProcess(cmd):
        return WorkerManager.__SubProcessManager.Submit(cmd)


def SubmitSubProcess(cmd):
    return WorkerManager.SubmitSubProcess(cmd)
