import json
import sys
import os


Renamed = {"Compare": {"ports": {"result": "output"}},
           "DasEval": {"ports": {"result": "output"}},
           "DasGet": {"ports": {"result": "output"}},
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
           "Selector": {"type": "ReRoute"},
           "RegexSelector": {"type": "RegexReRoute"},}


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("No file to patch")
    sys.exit(1)

  org = sys.argv[1]

  if len(sys.argv) == 3:
    new = sys.argv[2]
  else:
    name, ext = os.path.splitext(org)
    new = name + "_patch" + ext

  d = {}
  with open(org, "r") as f:
    d = json.load(f)
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


  with open(new, "w") as f:
    json.dump(d, f, indent=4)
