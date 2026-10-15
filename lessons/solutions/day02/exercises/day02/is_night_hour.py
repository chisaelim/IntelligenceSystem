def is_night(hour):
    """True from 22:00 until 05:59."""
    return hour >= 22 or hour < 6


for hour in (0, 5, 6, 12, 21, 22, 23):
    print(hour, "->", is_night(hour))
