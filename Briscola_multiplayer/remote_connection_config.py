import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ns_ip = s.getsockname()[0]
s.close()

server_address = {
    "ip": ns_ip,
    "port": 64339
}