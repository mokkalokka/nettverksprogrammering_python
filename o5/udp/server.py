import socket

WELCOME_MESSAGE = bytes("Welcome to the server\n\nThis server has the function to add or subtract two numbers\n"
                        "Usage: [sub | add] num_1 num_2\nexit to quit", "utf-8")

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)

print('waiting for connections')
data, address = sock.recvfrom(4096)
print('New connection: ', address)

print('Sending welcome message')
sock.sendto(WELCOME_MESSAGE, address)

while True:
    print('waiting to receive command')
    data, address = sock.recvfrom(4096)

    if data:
        dataStr = data.decode("utf-8")
        print("Client Says: " + dataStr)
        commands = dataStr.split(" ", 100)

        e = ""

        if (commands[0] != "sub" or commands[0] != "add") and commands.__len__() != 3:
            e = "error"

        if e == "":
            try:
                num_1 = int(commands[1])
                num_2 = int(commands[2])

            except ValueError as error:
                e = error

        if e != "":
            msg = "Invalid syntax, \nUsage: [sub | add] num_1 num_2"
        elif commands[0] == "sub":
            msg = str(num_1 - num_2)

        elif commands[0] == "add":
            msg = str(num_1 + num_2)

        sock.sendto(bytes(msg, "utf-8"), address)
