import socket
import threading

PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((socket.gethostname(), PORT))
s.listen(5)

print(f"Server is running, listening on port {PORT}")


def clients():
    while True:
        # now our endpoint knows about the OTHER endpoint.
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established.")
        clientsocket.send(bytes("Welcome to the server\n\n"
                                "This server has the function to add or subtract two numbers\n"
                                "Usage: [sub | add] num_1 num_2", "utf-8"))
        while True:
            try:
                data = clientsocket.recv(2048)
                dataStr = data.decode("utf-8")

                if not data:
                    break

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

                clientsocket.sendall(bytes(msg, "utf-8"))

            except socket.error:
                print("Error Occured.")
                break


threads = []
for i in range(5):
    threads.append(threading.Thread(target=clients))
    threads[i].start()



