#!/usr/bin/env python3

import socket
from socket import *
import time
from threading import Thread

car_ip = "10.0.0.50"
car_port = 23402
message = b'GATE CLOSED'

print("Start CROSS", flush=True)


class WarnCarThread:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        while self._running:
            sock2 = socket(AF_INET, SOCK_STREAM)
            server_address2 = (car_ip, car_port)
            try:
                sock2.connect(server_address2)
                while True:
                    if self._running:
                        sock2.sendall(message)
                    else:
                        break
                    time.sleep(1)
            except ConnectionRefusedError:
                print("CAR REFUSED", flush=True)
            except OSError:
                print("CAR OUT OF RANGE", flush=True)
            finally:
                sock2.close()
            time.sleep(1)


local_ip = "10.0.0.51"
local_port = 23401

sock = socket(AF_INET, SOCK_STREAM)
server_address = (local_ip, local_port)
sock.bind(server_address)
sock.listen(1)

while True:
    connection, client_address = sock.accept()
    connection.settimeout(5)
    print("timeout "+str(connection.gettimeout()), flush=True)
    c = WarnCarThread()
    try:
        print("CLOSE GATE", flush=True)
        t = Thread(target=c.run)
        t.start()
        # Signal termination
        while True:
            print("Start receive data", flush=True)
            data = connection.recv(16)
            print("Received data", flush=True)
            if not data:
                break
    except timeout:
        print("Connection timed out", flush=True)
        pass
    finally:
        # Clean up the connection
        connection.close()
        print("OPEN GATE", flush=True)
        c.terminate()
