import socket
import threading

PORT = 3000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('localhost', PORT))
s.listen(5)

print(f"Server is running, listening on port {PORT}")


def clients():
    while True:
        # Accepts new connection
        clientsocket, address = s.accept()
        print(f"Connection from {address} has been established.")

        content = "<!DOCTYPE html>" \
                  "<HTML>" \
                  "<body> " \
                  "WebSocket test page " \
                  "<script> let ws = new WebSocket('ws://localhost:3001'); " \
                  "ws.onmessage = event => alert('Message from server: ' + event.data); " \
                  "ws.onopen = () => ws.send('Hello from client!'); " \
                  "</script> " \
                  "</body>" \
                  "</HTML>"

        clientsocket.send(
            bytes('HTTP/1.1 200 OK\nContent-Length: ' + str(len(content)) + '\n\n' + content, "utf-8"))


threads = []
for i in range(5):
    threads.append(threading.Thread(target=clients))
threads[i].start()
