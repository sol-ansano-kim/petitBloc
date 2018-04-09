import os


def Run(path=None, contexts=[], parameters=[], blocks=False, query=False, info=None, maxProcess=1, verbose=1):
    from . import scene

    if blocks:
        return scene.BlockList()

    if info:
        return scene.BlockInfo(info)

    if (not path) or (not os.path.isfile(path)) or (os.path.splitext(path)[-1].lower() != ".blcs"):
        print("Invalid scene file : {}".format(path))
        return False

    if query:
        return scene.Query(path)

    return scene.Run(path, contexts=contexts, parameters=parameters, maxProcess=maxProcess, verbose=verbose)
