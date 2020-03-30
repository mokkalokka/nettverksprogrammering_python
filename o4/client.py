import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.connect((socket.gethostname(), 8080))

while True:
    msg = s.recv(2048)
    print(msg.decode("utf-8"))

    while msg != "":
        command = input("please enter command:\n")
        s.sendall(bytes(command, "utf-8"))

        msg = s.recv(1024)
        print(msg.decode("utf-8"))
