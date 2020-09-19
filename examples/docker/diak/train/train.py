import socket
import time

cross_ip = "10.0.0.51"
cross_port = 23401
message = b'Im here'

while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (cross_ip, cross_port)
    sock.connect(server_address)
    print("IN RANGE")
    try:
        while True:
            sock.sendall(message)
            time.sleep(1)

    finally:
        print("OUT OF RANGE")
        sock.close()
    time.sleep(5)
