import json

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

cfg["alert"]["min_severity"] = 3
cfg["zones"][0]["enabled"] = True

with open("config_test.json", "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
print("saved config_test.json")

with open("config_test.json", encoding="utf-8") as f:
    check = json.load(f)
print("min_severity is now", check["alert"]["min_severity"])
print("front_door enabled:", check["zones"][0]["enabled"])
