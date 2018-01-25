import os


def Run(path=None, multiProcessing=False, attrbutes=[]):
    from . import scene

    if (not path) or (not os.path.isfile(path)) or (os.path.splitext(path)[-1].lower() != ".blcs"):
        print("Invalid scene file : {}".format(path))
        return False

    return scene.Run(path, multiProcessing=multiProcessing, attrbutes=attrbutes)
