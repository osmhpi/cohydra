#!/usr/bin/env python3

import socket
import time
from threading import Thread

car_ip = "10.0.0.52"
car_port = 23402
message = b'GATE CLOSED'


class WarnCarThread:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (car_ip, car_port)
            try:
                sock.connect(server_address)
                while True:
                    if self._running:
                        sock.sendall(message)
                    else:
                        break
                    time.sleep(1)
            except ConnectionRefusedError:
                pass
            finally:
                sock.close()
            time.sleep(1)


local_ip = "127.0.0.1"
local_port = 23401

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (local_ip, local_port)
sock.bind(server_address)
sock.listen(1)

while True:
    connection, client_address = sock.accept()
    c = WarnCarThread()
    try:
        print("CLOSE GATE")
        t = Thread(target=c.run)
        t.start()
        # Signal termination
        while True:
            data = connection.recv(16)
            if not data:
                break

    finally:
        # Clean up the connection
        connection.close()
        print("OPEN GATE")
        c.terminate()
