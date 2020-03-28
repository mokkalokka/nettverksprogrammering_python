import socket
import threading

PORT = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('localhost', PORT))
s.listen(5)

print(f"Server is running, listening on port {PORT}")


def clients():
    while True:
        # Accepts new connection
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established.")

        data = clientsocket.recv(2048)
        header = data.decode("utf-8")
        print(header)

        clientsocket.send(bytes(
            "HTTP/1.0 200 OK \n"
            "Content-Type: text/html; charset=utf-8 \n"
            "\n"
            "<HTML><BODY>\n"
            "<H1>Welcome to my simple HTTP server</h1>\n"
            "Header fom client:\n"
            "<UL>\n"
            "<LI>" + header + "</LI>\n"
            "</UL>\n"
            "</BODY></HTML>", "utf-8")
        )


threads = []
for i in range(5):
    threads.append(threading.Thread(target=clients))
    threads[i].start()



