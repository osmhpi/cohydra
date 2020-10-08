import socket
import xmlrpc.client

print("Start CAR", flush=True)

local_ip = "10.0.0.50"
local_port = 23402

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (local_ip, local_port)
sock.bind(server_address)
sock.listen(1)

with xmlrpc.client.ServerProxy("http://172.17.0.1:23404/", allow_none=True) as traci:
    print("I CAN DRIVE", flush=True)
    while True:
        connection, client_address = sock.accept()
        try:
            print("I HAVE TO STOP", flush=True)
            traci.vehicle.setSpeed("car0", 0)
            while True:
                data = connection.recv(16)
                if not data:
                    break

        finally:
            # Clean up the connection
            connection.close()
            print("I CAN DRIVE", flush=True)
            traci.vehicle.setSpeed("car0", -1)
