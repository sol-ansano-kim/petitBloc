import os
from . import scene


def AllBlockTypes():
    return scene.AllBlockTypes()


def BlockInfo(blockName):
    return scene.BlockInfo(blockName)


def GetParams(path, block=None):
    return scene.GetParams(path, block=block)


def GetContextParams(path):
    return scene.GetContextParams(path)


def GetConnections(path):
    return scene.GetConnections(path)


def GetBlocks(path):
    return scene.GetBlocks(path)



# TODO : Read and Write just handle json file.
# and GUI do almost same thing with scene.__read()
# have to make these more clear before provide these functions
# def Read(path):
#     return scene.Read(path)


# def Write(path, data):
#     return scene.Write(path, data)


def QueryScene(path):
    return scene.QueryScene(path)


def Run(path=None, contexts=None, parameters=None, blocks=False, query=False, info=None, maxProcess=1, verbose=1):
    if blocks:
        print("'blocks' options is deprecated, please use 'AllBlockTypes' function instead")
        return AllBlockTypes()

    if info:
        print("'info' options is deprecated, please use 'BlockInfo' function instead")
        return BlockInfo(info)

    if query:
        print("'info' options is deprecated, please use 'QueryScene' function instead")
        return QueryScene(path)

    return scene.Run(path, contexts=contexts, parameters=parameters, maxProcess=maxProcess, verbose=verbose)
