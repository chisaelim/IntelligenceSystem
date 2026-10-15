width = int(input("Frame width in pixels: "))
height = int(input("Frame height in pixels: "))
fps = int(input("Frames per second: "))

pixels = width * height
bytes_per_frame = pixels * 3  # 3 colour values (blue, green, red), 1 byte each
mb_per_frame = bytes_per_frame / 1024 / 1024
mb_per_second = mb_per_frame * fps
gb_per_hour = mb_per_second * 3600 / 1024

print(f"One frame has {pixels:,} pixels")
print(f"One frame needs {mb_per_frame:.2f} MB")
print(f"One second of video needs {mb_per_second:.1f} MB")
print(f"One hour of video needs {gb_per_hour:.0f} GB (before compression)")
