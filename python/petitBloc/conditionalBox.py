from . import box
from . import workerManager


class ConditionalBox(box.Box):
    def __init__(self, name="", parent=None):
        super(ConditionalBox, self).__init__(name=name, parent=parent)
        self.__condtion = None

    def __str__(self):
        return "ConditionalBox<'{}'>".format(self.name())

    def clear(self):
        if self.__condtion is not None:
            workerManager.WorkerManager.DeleteValue(self.__condtion)
            self.__condtion = None

        super(ConditionalBox, self).clear()

    def activate(self):
        self.__condtion = workerManager.WorkerManager.CreateValue("i", 0)

        super(ConditionalBox, self).activate()
        self.resetState()

    def isWaiting(self):
        if self.__condtion is None:
            return super(ConditionalBox, self).isWaiting()

        return self.__condtion.value is 0

    def terminate(self, success=True):
        if self.__condtion is not None:
            v = self.__condtion.value
            self.clear()
            super(ConditionalBox, self).terminate()

            if not v:
                self.resetState()

        else:
            super(ConditionalBox, self).terminate(success=success)

    def initialize(self):
        self.addInput(bool, "condition")

    def run(self):
        con = self.input("condition").receive()

        if con.isEOP():
            return False

        v = con.value()
        con.drop()
        self.__condtion.value = 1 if v else 0
