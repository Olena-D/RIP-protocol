###########################################################################
#                                                                         #
# "Sender" Class is responsible for constructing and sending individual   #
# messages for each neighbour. It uses principle of split horizon with    #
# poisoned reverse to substitute one metric for infinity.                 #
#                                                                         #
# Takes instances of "DaemonConfig" class and "Translator" class          #
# as arguments                                                            #
#                                                                         #
# The class has 2 methods - one private and one public                    #
#                                                                         # 
# "send" method takes a routing table as a parameter,                     #
# it constructs a message that is a dictionary with                       #
# neighbour's ports as keys and individualized packets as values          #
# ex: message = {port: packet}                                            #
#                                                                         #
# "send" method utilizes private method "pack" to make                    #
# individually designed packets for each neighbour                        #
#                                                                         #
###########################################################################

import socket


class Sender(object):
    def __init__(self, cfg, translator):
        self.__timeout = 1
        self.__myId = cfg.getRouterId()
        self.__outputs = cfg.getOutputs()
        self.__translator = translator

    def send(self, table):
        message = {}
        for output in self.__outputs:
            neighbour = output["neighbourId"]
            metric = output["metric"]
            port = output["port"]

            message[port] = self.__pack(table, neighbour, metric)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.__timeout)

        for port, packet in message.items():
            sock.sendto(packet, ('127.0.0.1', port))
        sock.close()

    def __pack(self, table, neighbour, cost):
        entry = {}

        if not neighbour in table:
            entry[neighbour] = cost

        for route, value in table.items():
            if route != neighbour and value.neighbour == neighbour:
                entry[route] = 16
                continue
            entry[route] = value.metric

        packet = self.__translator.pack(self.__myId, entry)
        return packet
