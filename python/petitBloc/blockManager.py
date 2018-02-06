import imp
import os
from . import core
from . import box
from . import util


class BlockManager(object):
    __Instance = None

    def __new__(self):
        if BlockManager.__Instance is None:
            BlockManager.__Instance = super(BlockManager, self).__new__(self)
            BlockManager.__Instance.reload()

        return BlockManager.__Instance

    def __init__(self):
        super(BlockManager, self).__init__()

    def reload(self):
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
        return self.__blocks.get(name, {}).get("class")

    def config(self, name):
        return self.__blocks.get(name, {}).get("config", {})

    def blockTree(self):
        tree = {}

        for b, v in self.__blocks.iteritems():
            category = v.get("config", {}).get("category", "Not Classified")
            if not tree.has_key(category):
                tree[category] = []

            tree[category].append(b)

        return tree

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
        self.__blocks["Box"] = {"class": box.Box, "config": {"category": "Scene"}}
        self.__blocks["SceneContext"] = {"class": box.SceneContext, "config": {"category": "Scene"}}

        block_path = os.environ.get("PETITBLOC_BLOCK_PATH", "")
        built_in = os.path.abspath(os.path.join(__file__, "../blocks")).replace("\\", "/")

        for block_dir in [built_in] + filter(lambda x: x, block_path.split(os.pathsep)):
            if not os.path.isdir(block_dir):
                continue

            for fp in os.listdir(block_dir):
                if os.path.splitext(fp)[-1].lower() == ".py":
                    py_path = os.path.abspath(os.path.join(block_dir, fp)).replace("\\", "/")
                    if py_path in self.__loaded:
                        continue

                    self.__loaded.append(py_path)

                    configs = {}
                    config_path = os.path.splitext(py_path)[0] + ".config"
                    if os.path.isfile(config_path):
                        configs = util.LoadConfig(config_path)

                    module = self.importModule(py_path)

                    for cont_name in dir(module):
                        if self.__blocks.has_key(cont_name):
                            continue

                        content = getattr(module, cont_name)

                        if not hasattr(content, "getSchedule"):
                            continue

                        if issubclass(content, core.ComponentBase):
                            self.__blocks[cont_name] = {"class": content, "config": configs.get(cont_name, {})}
                            self.__modules.append(module)

    def importModule(self, path):
        module = None

        try:
            module = imp.load_source(os.path.splitext(os.path.basename(path))[0], path)
        except Exception as e:
            return None

        return module