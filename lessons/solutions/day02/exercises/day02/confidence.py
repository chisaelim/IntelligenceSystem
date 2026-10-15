CONFIDENCE_LIMIT = 0.45  # the same number as "confidence" in config.json

score = float(input("Detection confidence (0 to 1): "))

if score < CONFIDENCE_LIMIT:
    print("ignore: too uncertain")
elif score < 0.70:
    print("medium: probably correct")
else:
    print("high: very likely correct")
