from packet import packet
from ttnmon import ttnmon
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 1700

with open("mailto.txt") as mail:
    mailto = mail.read()[0:-1] #Remove \n at line end

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
packet_handler = ttnmon(mailto)
packet_handler.startThread()

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    pkt = packet(data)
    packet_handler.add(pkt)
