###--Test--###

import struct
import socket


def send(packet):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.sendto(packet, ('127.0.0.1', 6011))
    sock.close()


command = input("command > ")
while command != 'q':
    if command == 's':
        send(struct.pack('>2hi2i4q2i4q', 2, 2, 6,
                         2, 0, 8, 0, 0, 4, 2, 0, 1, 0, 0, 5))
        print("Command 'send' completed")

    if command == 'i':
        send(struct.pack('>2h3i4q', 2, 2, 5, 2, 0, 8, 0, 0, 2))
        print("Command 'send invalid' completed")

    if command == 'u':
        send(struct.pack('>2hi2i4q2i4q', 2, 2, 2,
                         2, 0, 8, 0, 0, 2, 2, 0, 1, 0, 0, 1))
        print("Command 'send better route' completed")

    if command == 'b':
        send(struct.pack('>2hi2i4q2i4q', 2, 2, 2,
                         2, 0, 8, 0, 0, 6, 2, 0, 1, 0, 0, 1))
        print("Command 'send worse metric from the same neighbour' completed")

    if command == 'v':
        send(struct.pack('>2hi2i4q2i4q', 2, 2, 6,
                         2, 0, 2, 0, 0, 6, 2, 0, 1, 0, 0, 5))
        print("Command 'send worse metric' completed")

    if command == 'd':
        send(struct.pack('>2hi2i4q2i4q', 2, 2, 2,
                         2, 0, 8, 0, 0, 16, 2, 0, 1, 0, 0, 1))
        print("Command 'send dead link' completed")

    if command == 'f':
        send(struct.pack('>2hi2i4q2i4q2i4q', 2, 2, 6, 2, 0, 1,
                         0, 0, 5, 2, 0, 7, 0, 0, 16, 2, 0, 8, 0, 0, 16))
        print("Command 'send dead link' completed")

    if command == 'h':
        send(struct.pack('>2hi', 2, 2, 6))
        print("Command 'send header' completed")

    command = input("command > ")
