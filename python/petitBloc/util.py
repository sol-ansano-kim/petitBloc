import re
import json


ReConvention = re.compile("^[a-zA-Z][a-zA-Z0-9_]*$")
ReForbiddenName = re.compile("[^a-zA-z0-9_]")
ReNumber = re.compile("[0-9]+$")


def ValidateName(name):
    return True if ReConvention.match(name) else False


def GetUniqueName(name, all_names):
    if name not in all_names:
        return name

    pure = ReNumber.sub("", name)
    pattern = re.compile("^{}([0-9]+)$".format(pure))

    idx = 0
    for n in all_names:
        rgx = pattern.match(n)
        if rgx:
            new_idx = int(rgx.group(1))
            if new_idx > idx:
                idx = new_idx

    return "{}{}".format(pure, idx + 1)


def LoadConfig(filePath):
    data = {}

    try:
        with open(filePath, 'r') as myfile:
            fileString = myfile.read()

            cleanString = re.sub('//.*?\n|/\*.*?\*/', '', fileString, re.S)

            data = json.loads(cleanString)
    except:
        return {}
    else:
        return data
