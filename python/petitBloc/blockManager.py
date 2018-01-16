import imp
import os
from . import core
from . import block
from . import box


class BlockManager(object):
    def __init__(self):
        super(BlockManager, self).__init__()
        self.__blocks = {}
        self.__searchBlocks()

    def blockNames(self):
        keys = sorted(self.__blocks.keys())
        return keys

    def hasBlock(self, name):
        return self.__blocks.has_key(name)

    def block(self, name):
        return self.__blocks.get(name)

    def __searchBlocks(self):
        self.__blocks["Box"] = box.Box

        block_path = os.environ.get("PETITBLOC_BLOCK_PATH", "")
        for block_dir in filter(lambda x: x, block_path.split(os.pathsep)):
            if not os.path.isdir(block_dir):
                continue

            for fp in os.listdir(block_dir):
                if os.path.splitext(fp)[-1].lower() == ".py":
                    module = self.importModule(os.path.join(block_dir, fp))
                    for cont_name in dir(module):
                        if self.__blocks.has_key(cont_name):
                            continue

                        content = getattr(module, cont_name)

                        if not hasattr(content, "getSchedule"):
                            continue

                        if issubclass(content, core.ComponentBase):
                            self.__blocks[cont_name] = content

    def importModule(self, path):
        module = None

        try:
            module = imp.load_source(os.path.splitext(os.path.basename(path))[0], path)
        except Exception as e:
            return None

        return module