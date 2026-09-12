import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# send the data to the ip and port
client.sendto("hello from client".encode(), ("127.0.0.1", 999))

# receive the data and addr
data, addr = client.recvfrom(1024)

# decode and print the data
print(data.decode())