from packet import packet
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 1700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    pkt = packet(data)
    if (pkt.type != packet.INVALID):
        print (pkt.gateway_addr)
