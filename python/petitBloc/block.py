from . import component


class Block(component.Component):
    def __init__(self, name="", parent=None):
        super(Block, self).__init__(name=name, parent=parent)

    def run(self):
        # override this method
        pass

    def initialize(self):
        # override this method
        pass
