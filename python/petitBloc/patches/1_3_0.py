Renamed = {"Compare": {"ports": {"result": "output"}},
           "DasEval": {"ports": {"result": "output"}},
           "DasGet": {"ports": {"result": "output"}},
           "DasNew": {"ports": {"outDasObj": "dasObj", "output": "dasObj"}},
           "DasValidate": {"ports": {"schemed": "output"}},
           "Divide": {"ports": {"result": "output"}},
           "Minus": {"ports": {"result": "output"}},
           "Multiply": {"ports": {"result": "output"}},
           "Plus": {"ports": {"result": "output"}},
           "RegexFindAll": {"ports": {"result": "output"}},
           "RegexSearch": {"ports": {"result": "output"}},
           "RegexSub": {"ports": {"result": "output"}},
           "StringAdd": {"ports": {"result": "output"}},
           "StringCount": {"ports": {"result": "output"}},
           "StringReplace": {"ports": {"result": "output"}},
           "Selector": {"type": "Fork"},
           "ReRoute": {"type": "Fork"},
           "ListLength": {"ports": {"len": "length"}},
           "ListAppend": {"ports": {"list": "inList", "output": "outList"}},
           "ListRemove": {"ports": {"list": "inList", "output": "outList"}},
           "ListExtend": {"ports": {"extended": "output"}},
           "ListHas": {"ports": {"output": "has"}},
           "DictHas": {"ports": {"output": "has"}},
           "DictUpdate": {"ports": {"outDict": "output"}},
           "RegexSelector": {"type": "RegexFork"},
           "RegexReRoute": {"type": "RegexFork"},
           "FileRead": {"ports": {"data": "line"}},
           "FileWrite": {"ports": {"data": "line"}},
           "FloatToString": {"params": {"demical": "decimal"}}, }


def Patch(d):
  blocks = {}

  for b in d.get("blocks", []):
    blocks[b["path"]] = b

  for con in d.get("connections", []):
    block, port = con["path"].split(".")
    if block in blocks:
      bt = blocks[block]["type"]
      if bt in Renamed and port in Renamed[bt].get("ports", {}):
        con["path"] = block + "." + Renamed[bt]["ports"][port]

    block, port = con["src"].split(".")
    if block in blocks:
      bt = blocks[block]["type"]
      if bt in Renamed and port in Renamed[bt].get("ports", {}):
        con["src"] = block + "." + Renamed[bt]["ports"][port]

  for b in d.get("blocks", []):
    bt = b["type"]
    if bt in Renamed and "type" in Renamed[bt]:
      b["type"] = Renamed[bt]["type"]

    if "params" in b and bt in Renamed and "params" in Renamed[bt]:
      for be, af in Renamed[bt]["params"].items():
        if be in b["params"]:
          b["params"][af] = b["params"].pop(be)
