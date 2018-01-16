from . import processManager
from . import threadManager


class WorkerManager(object):
    __UseProcess = True

    @staticmethod
    def SetUseProcess(value):
        if WorkerManager.__UseProcess != value:
            if WorkerManager.__UseProcess:
                processManager.QueueManager.Reset()
                processManager.ProcessManager.Reset()
            else:
                threadManager.QueueManager.Reset()
                threadManager.ThreadManager.Reset()

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
            return processManager.QueueManager.DeleteQueue(q)
        else:
            return threadManager.QueueManager.DeleteQueue(q)

    @staticmethod
    def RunSchedule(schedule, maxProcess=0):
        if WorkerManager.UseProcess():
            processManager.RunSchedule(schedule, maxProcess=0)
        else:
            threadManager.RunSchedule(schedule, maxProcess=0)



