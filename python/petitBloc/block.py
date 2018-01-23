from . import component
from . import util


class Block(component.Component):
    def __init__(self, name="", parent=None):
        super(Block, self).__init__(name=name, parent=parent)

    def process(self):
        # override this method
        return False

    def initialize(self):
        # override this method
        pass
