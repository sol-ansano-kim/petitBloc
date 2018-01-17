from . import processManager
from . import threadManager


class WorkerManager(object):
    __UseProcess = True

    @staticmethod
    def SetUseProcess(value):
        if WorkerManager.__UseProcess != value:
            WorkerManager.ResetQueue()
            WorkerManager.ResetProcess()

        WorkerManager.__UseProcess = value

    @staticmethod
    def UseProcess():
        return WorkerManager.__UseProcess

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
    def RunSchedule(schedule, maxProcess=0):
        if WorkerManager.UseProcess():
            processManager.RunSchedule(schedule, maxProcess=0)
        else:
            threadManager.RunSchedule(schedule, maxProcess=0)

    @staticmethod
    def QueueCount():
        if WorkerManager.UseProcess():
            return processManager.QueueManager.Count()
        else:
            return threadManager.QueueManager.Count()

    @staticmethod
    def ProcessCount():
        if WorkerManager.UseProcess():
            return processManager.ProcessManager.Count()
        else:
            return threadManager.ThreadManager.Count()

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
