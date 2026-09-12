import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 999))

client.send("hello from client".encode())
print(client.recv(1024).decode())