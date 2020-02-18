import os
import re
import imp


class Patch(object):
    Patches = None

    @staticmethod
    def __CollectPatches():
        Patch.Patches = []

        for f in os.listdir(os.path.dirname(__file__)):
            sn = os.path.splitext(f)[0]
            res = re.search("^(?P<major>[0-9]+)[_](?P<minor>[0-9]+)[_](?P<patch>[0-9]+)$", sn)
            if res is None:
                continue

            p = Patch(int(res.group("major")), int(res.group("minor")), int(res.group("patch")), os.path.abspath(os.path.join(os.path.dirname(__file__), f)))
            if not p.isValid():
                continue

            if p in Patch.Patches:
                continue

            Patch.Patches.append(p)

        Patch.Patches.sort()

    @staticmethod
    def GetPatches():
        if Patch.Patches is None:
            Patch.__CollectPatches()

        return Patch.Patches

    @staticmethod
    def __getOthesVersion(other):
        if isinstance(other, Patch):
            return (other.__major, other.__minor, other.__patch)

        if isinstance(other, basestring):
            res = re.search("^(?P<major>[0-9]+)[.](?P<minor>[0-9]+)[.](?P<patch>[0-9]+)$", other)
            if not res:
                return (None, None, None)

            return int(res.group("major")), int(res.group("minor")), int(res.group("patch"))

        return (None, None, None)

    def __eq__(self, other):
        major, minor, patch = Patch.__getOthesVersion(other)

        if major is None or minor is None or patch is None:
            return False

        return self.__major == major and self.__minor == minor and self.__patch == patch

    def __lt__(self, other):
        major, minor, patch = Patch.__getOthesVersion(other)

        if major is None or minor is None or patch is None:
            return False

        if self.__major == major:
            if self.__minor == minor:
                return self.__patch < patch
            else:
                return self.__minor < minor
        else:
            return self.__major < major

    def __gt__(self, other):
        major, minor, patch = Patch.__getOthesVersion(other)

        if major is None or minor is None or patch is None:
            return False

        if self.__major == major:
            if self.__minor == minor:
                return self.__patch > patch
            else:
                return self.__minor > minor
        else:
            return self.__major > major

    def __ge__(self, other):
        major, minor, patch = Patch.__getOthesVersion(other)

        if major is None or minor is None or patch is None:
            return False

        if self.__major == major:
            if self.__minor == minor:
                return self.__patch >= patch
            else:
                return self.__minor >= minor
        else:
            return self.__major >= major

    def __le__(self, other):
        major, minor, patch = Patch.__getOthesVersion(other)

        if major is None or minor is None or patch is None:
            return False

        if self.__major == major:
            if self.__minor == minor:
                return self.__patch <= patch
            else:
                return self.__minor <= minor
        else:
            return self.__major <= major

    def __repr__(self):
        return "<Patch'{}.{}.{}'>".format(self.__major, self.__minor, self.__patch)

    def __init__(self, major, minor, patch, path):
        super(Patch, self).__init__()
        self.__is_valid = True
        self.__major = major
        self.__minor = minor
        self.__patch = patch
        self.__func = None

        try:
            sn = os.path.splitext(os.path.basename(path))[0]
            modle = imp.load_source("petitbloc_patch_{}".format(sn), path)
            self.__func = modle.Patch
        except:
            self.__is_valid = False

    def majorVersion(self):
        return self.__major

    def minorVersion(self):
        return self.__minor

    def patchVersion(self):
        return self.__patch

    def isValid(self):
        return self.__is_valid

    def patch(self, data):
        if not self.__is_valid:
            return

        self.__func(data)


def AttachPatch(data):
    version = data.get("apiVersion", "0.1.0")
    for p in Patch.GetPatches():
        if version >= p:
            continue

        print("Patch : {}.{}.{}".format(p.majorVersion(), p.minorVersion(), p.patchVersion()))
        p.patch(data)
