import imp
import os
from . import core
from . import box


class BlockManager(object):
    __Instance = None

    def __new__(self):
        if BlockManager.__Instance is None:
            BlockManager.__Instance = super(BlockManager, self).__new__(self)

        return BlockManager.__Instance

    def __init__(self):
        super(BlockManager, self).__init__()
        self.__blocks = {}
        self.__modules = []
        self.__loaded = []
        self.__finded_class = {"bool": bool, "int": int, "float": float, "str": str}
        self.__searchBlocks()

    def blockNames(self):
        keys = sorted(self.__blocks.keys())
        return keys

    def hasBlock(self, name):
        return self.__blocks.has_key(name)

    def block(self, name):
        return self.__blocks.get(name)

    def findObjectClass(self, name):
        cls = self.__finded_class.get(name, None)
        if cls is not None:
            return cls

        for mod in self.__modules:
            if hasattr(mod, name):
                self.__finded_class[name] = getattr(mod, name)
                return getattr(mod, name)

            for cont_name in dir(mod):
                content = getattr(mod, cont_name)
                if not hasattr(content, "__file__"):
                    continue

                if hasattr(content, name):
                    self.__finded_class[name] = getattr(content, name)
                    return getattr(content, name)

        return None

    def __searchBlocks(self):
        self.__blocks["Box"] = box.Box
        self.__blocks["SceneContext"] = box.SceneContext

        block_path = os.environ.get("PETITBLOC_BLOCK_PATH", "")
        for block_dir in filter(lambda x: x, block_path.split(os.pathsep)):
            if not os.path.isdir(block_dir):
                continue

            for fp in os.listdir(block_dir):
                if os.path.splitext(fp)[-1].lower() == ".py":
                    py_path = os.path.abspath(os.path.join(block_dir, fp))
                    if py_path in self.__loaded:
                        continue

                    self.__loaded.append(py_path)

                    module = self.importModule(py_path)

                    for cont_name in dir(module):
                        if self.__blocks.has_key(cont_name):
                            continue

                        content = getattr(module, cont_name)

                        if not hasattr(content, "getSchedule"):
                            continue

                        if issubclass(content, core.ComponentBase):
                            self.__blocks[cont_name] = content
                            self.__modules.append(module)

    def importModule(self, path):
        module = None

        try:
            module = imp.load_source(os.path.splitext(os.path.basename(path))[0], path)
        except Exception as e:
            return None

        return module