import socket
import time

cross_ip = "10.0.0.51"
cross_port = 23401
message = b'Im here'

print("Start TRAIN", flush=True)

while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (cross_ip, cross_port)
        sock.connect(server_address)
        print("IN RANGE", flush=True)
        try:
            while True:
                sock.sendall(message)
                print("SEND Im here", flush=True)
                time.sleep(1)

        finally:
            print("OUT OF RANGE", flush=True)
            sock.close()
    except ConnectionRefusedError:
        print("OUT OF RANGE (CR)", flush=True)
    except OSError:
        print("OUT OF RANGE (OS)", flush=True)
    time.sleep(1)
