import json

with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

print("watching:", ", ".join(cfg["watch_classes"]))
print("night hours:", cfg["night_hours"][0], "to", cfg["night_hours"][1])
print("alert when severity >=", cfg["alert"]["min_severity"])

print("\nSeverity by label:")
for label, severity in cfg["label_severity"].items():
    print(f"  {label:10} {severity}")

enabled = [z["name"] for z in cfg["zones"] if z["enabled"]]
print("\nenabled zones:", enabled if enabled else "none")
