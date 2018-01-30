import os


def Run(path=None, multiProcessing=False, contexts=[], parameters=[], query=False, info=None, verbose=1):
    from . import scene

    if info:
        return scene.BlockInfo(info)

    if (not path) or (not os.path.isfile(path)) or (os.path.splitext(path)[-1].lower() != ".blcs"):
        print("Invalid scene file : {}".format(path))
        return False

    if query:
        return scene.Query(path)

    return scene.Run(path, contexts=contexts, parameters=parameters, verbose=verbose)
