import socket
import threading
from hashlib import sha1
from base64 import b64encode

PORT = 3001

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

        data = clientsocket.recv(2048)
        header = data.decode("utf-8")
        key = get_websocket_key(header)

        content = ("HTTP/1.1 101 Switching Protocols",
                   "Upgrade: websocket",
                   "Connection: Upgrade",
                   "Sec-WebSocket-Accept: {key}\r\n\r\n")

        response_key = accept_handshake(key)
        print("Response key: " + response_key)
        res = '\r\n'.join(content).format(key=response_key)

        clientsocket.send(bytes(res, "utf-8"))

        client_sockets.append(clientsocket)

        while True:
            try:
                data = clientsocket.recv(1024)
                data_bytes = bytearray(data)

                if len(data_bytes) > 2 and data_bytes[0] == 129:
                    decoded_msg = decode_websocket_data(data)
                    print(f"Recieved new message from {address}: \nRAW data:{data}\nDecoded: {decoded_msg}")

                    echo = f"{address[0]}, {address[1]}: " + decoded_msg
                    echo_all(format_payload(echo))
            except ConnectionResetError:
                print(f"{address} disconnected")
                break


def echo_all(payload):
    for client_socket in client_sockets:
        try:
            client_socket.send(payload)
        except BrokenPipeError:
            client_sockets.remove(client_socket)


def get_websocket_key(header):
    for l in header.splitlines():
        w = l.split(" ")
        if w[0] == "Sec-WebSocket-Key:":
            return w[1]


def format_payload(data):
    data = bytearray(data.encode())
    txt_code = 129  # 0x81 in hex
    length = len(data)
    payload = [txt_code, length]

    for byte in data:
        payload.append(byte)

    return bytearray(payload)


def decode_websocket_data(data):
    data_bytes = bytearray(data)
    length = data_bytes[1] & 127
    maskStart = 2
    dataStart = maskStart + 4
    msg = ""

    for i in range(dataStart, dataStart + length):
        byte = data_bytes[i] ^ data_bytes[maskStart + ((i - dataStart) % 4)]
        msg += chr(byte)
    return msg


def accept_handshake(key):
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    response_key = b64encode(sha1((key + GUID).encode("utf-8")).digest())
    return str(response_key, "utf-8")


client_sockets = []
threads = []
for i in range(5):
    threads.append(threading.Thread(target=clients))
    threads[i].start()
