import os
from . import version


SceneModule = None


def _getSceneModule():
    global SceneModule

    if SceneModule is None:
        from . import scene as SceneModule

    return SceneModule


def Version():
    return version.version()


def AllBlockTypes():
    return _getSceneModule().AllBlockTypes()


def BlockInfo(blockName):
    return _getSceneModule().BlockInfo(blockName)


def GetParams(path, block=None):
    return _getSceneModule().GetParams(path, block=block)


def GetContextParams(path):
    return _getSceneModule().GetContextParams(path)


def GetConnections(path):
    return _getSceneModule().GetConnections(path)


def GetBlocks(path):
    return _getSceneModule().GetBlocks(path)



# TODO : Read and Write just handle json file.
# and GUI do almost same thing with _getSceneModule().__read()
# have to make these more clear before provide these functions
# def Read(path):
#     return _getSceneModule().Read(path)


# def Write(path, data):
#     return _getSceneModule().Write(path, data)


def QueryScene(path):
    return _getSceneModule().QueryScene(path)


def Run(path=None, contexts=None, parameters=None, blocks=False, query=False, info=None, maxProcess=1, verbose=2):
    if blocks:
        print("'blocks' options is deprecated, please use 'AllBlockTypes' function instead")
        return AllBlockTypes()

    if info:
        print("'info' options is deprecated, please use 'BlockInfo' function instead")
        return BlockInfo(info)

    if query:
        print("'info' options is deprecated, please use 'QueryScene' function instead")
        return QueryScene(path)

    return _getSceneModule().Run(path, contexts=contexts, parameters=parameters, maxProcess=maxProcess, verbose=verbose)
