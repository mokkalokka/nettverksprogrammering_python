import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 3030))

while True:
    msg = s.recv(2048)
    print(msg.decode("utf-8"))

    while msg != "":
        command = input("\nplease enter command:\n")
        s.sendall(bytes(command, "utf-8"))

        msg = s.recv(1024)
        print(msg.decode("utf-8"))