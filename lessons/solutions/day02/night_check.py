hour = int(input("Hour of the day (0 to 23): "))

if hour >= 22 or hour < 6:
    print("night")
else:
    print("day")
