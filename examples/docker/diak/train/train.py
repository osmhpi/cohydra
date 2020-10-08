import socket
import time

cross_ip = "10.0.0.51"
cross_port = 23401
message = b'Im here'

print("Start TRAIN", flush=True)

while True:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        server_address = (cross_ip, cross_port)
        sock.connect(server_address)
        try:
            while True:
                sock.sendall(message)
                data = sock.recv(16)
                if not data:
                    break
                time.sleep(0.5)

        finally:
            sock.close()
    except ConnectionRefusedError:
        pass
    except OSError:
        pass
    time.sleep(0.5)
