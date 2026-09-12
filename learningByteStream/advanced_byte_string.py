import struct

# sample data 
company = b"Nvidia"
day, month, year = 13, 6, 2024
is_good = True

byte_stream = struct.pack("6s 3i ?", company, day, month, year, is_good)
print(byte_stream)