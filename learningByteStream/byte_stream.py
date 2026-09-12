import struct


byte_stream = struct.pack("iii", 10, 14, 30)
print(struct.calcsize("Q"))
print(byte_stream)

# a, b, c = struct.unpack("3i",byte_stream)

a, b, c = struct.unpack("iii",byte_stream)
print(f"\n{a} {b} {c}")