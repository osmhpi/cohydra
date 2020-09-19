import socket

print("Start CAR", flush=True)

local_ip = "10.0.0.50"
local_port = 23402

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (local_ip, local_port)
sock.bind(server_address)
sock.listen(1)

print("I CAN DRIVE", flush=True)
while True:
    connection, client_address = sock.accept()
    try:
        print("I HAVE TO STOP", flush=True)
        while True:
            data = connection.recv(16)
            if not data:
                break

    finally:
        # Clean up the connection
        connection.close()
        print("I CAN DRIVE", flush=True)
