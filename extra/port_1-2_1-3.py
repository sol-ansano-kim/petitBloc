import json
import sys
import os


Renamed = {"Compare": {"result": "output"},
           "DasEval": {"result": "output"},
           "DasGet": {"result": "output"},
           "Divide": {"result": "output"},
           "Minus": {"result": "output"},
           "Multiply": {"result": "output"},
           "Plus": {"result": "output"},
           "RegexFindAll": {"result": "output"},
           "RegexSearch": {"result": "output"},
           "RegexSub": {"result": "output"},
           "StringAdd": {"result": "output"},
           "StringCount": {"result": "output"},
           "StringReplace": {"result": "output"}}


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
        if bt in Renamed and port in Renamed[bt]:
          con["path"] = block + "." + Renamed[bt][port]

      block, port = con["src"].split(".")
      if block in blocks:
        bt = blocks[block]["type"]
        if bt in Renamed and port in Renamed[bt]:
          con["src"] = block + "." + Renamed[bt][port]

  with open(new, "w") as f:
    json.dump(d, f, indent=4)
