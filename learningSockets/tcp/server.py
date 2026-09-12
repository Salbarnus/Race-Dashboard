import socket

# create a server type of internet and tcp
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the server to a ip
# keep in mind it takes a tuple as input
server.bind(("127.0.0.1", 999))

# server listens to max 5 connections
server.listen(5)

while True:
    # client is an instance of the actual client and addr is the ip of the client
    client, addr = server.accept()
    print(client)
    print(addr)

    # receive 1024 bytes and decode the message
    print(client.recv(1024).decode())

    client.send("hello from server".encode())