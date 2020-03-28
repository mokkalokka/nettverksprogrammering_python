import socket

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)

# Send data
print('Trying to connect')
sent = sock.sendto(bytes("connect", "utf-8"), server_address)

while True:
    # Receive response
    data, server = sock.recvfrom(4096)
    print(data.decode("utf-8"))
    if data:
        command = input("Please enter command:\n")
        if command == "exit":
            break
        sock.sendto(bytes(command, "utf-8"), server_address)

print('closing socket')
sock.close()
