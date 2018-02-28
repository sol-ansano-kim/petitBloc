from maya import cmds
from maya import utils


def ExecuteFunction(func, *args, **kwargs):
    return utils.executeInMainThreadWithResult(func, *args, **kwargs)
