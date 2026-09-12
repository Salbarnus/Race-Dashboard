import socket

# create a server type of internet and udp
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind the server to a ip
# keep in mind it takes a tuple as input
server.bind(("127.0.0.1", 999))


while True:
    # in case of udp just recieve the message and addr in the form of a tuple
    data, addr = server.recvfrom(1024)

    print(data.decode())

    server.sendto("hello from server".encode(), addr)