######################################################################################
#                                                                                    #
# Translator Class is responsible for:                                               #
# - unpacking and validation of incomming RIP messages                               #
# - packing outgoing RIP messages                                                    #
#                                                                                    #   
# Incoming message from a peer daemon is a bytearray                                 #
# For example:                                                                       #
# b'\x00\x02\x00\x02\x00\x00\x00\x02        Header Part (command, version, routerId) #
# \x00\x00\x00\x02\x00\x00\x00\x00          Address Family, Must be zero fields      #
# \x00\x00\x00\x00\x00\x00\x00\x01          Destination address                      #
# \x00\x00\x00\x00\x00\x00\x00\x00          Must be zero                             #
# \x00\x00\x00\x00\x00\x00\x00\x00          Must be zero                             #
# \x00\x00\x00\x00\x00\x00\x00\x02          Metric                                   #
# \x00\x00\x00\x02\x00\x00\x00\x00          Address Family, Must be zero fields      #
# \x00\x00\x00\x00\x00\x00\x00\x03          Destination address                      #
# \x00\x00\x00\x00\x00\x00\x00\x00          Must be zero                             #
# \x00\x00\x00\x00\x00\x00\x00\x00          Must be zero                             #
# \x00\x00\x00\x00\x00\x00\x00\x04'         Metric                                   #
#                                                                                    #
# unpack method returns a tuple of 2 elements:                                       #
# 1 - an error message if any or None                                                #
# 2 - data in form of another tuple (2, {1: 2, 4: 6})                                #
#       if no errors were encountered or None                                        #
# first element of which is an Id of a peer router, which sent a message             #
# second element is a dictionary with destination address as a key                   #
# and metric as a value                                                              #
#                                                                                    #
# pack method takes 2 arguments:                                                     #
# router Id, which will go into routerId field of the header                         #
# and a dictionary containing destination addresses as keys and metrics as values    #
#                                                                                    #
# ####################################################################################

import struct


class Translator(object):
    def __init__(self):
        self.__command = 0x0002
        self.__version = 0x0002
        self.__bufferSize = 504

    def getBufferSize(self):
        return self.__bufferSize

    def pack(self, routerId, routes):
        message = struct.pack('>2hi', self.__command, self.__version, routerId)
        for destId, metric in routes.items():
            message += struct.pack('>2i4q', 2, 0, destId, 0, 0, metric)

        return message

    def unpack(self, data, neighbourIds):
        if len(data) < 8:
            return "The packet should have at least 4 bytes of header length", None

        command, version, neighbourId = struct.unpack('>2hi', data[:8])
        if command != self.__command:
            return "The packet 'command' field is incorrect", None
        if version != self.__version:
            return "The packet 'version' field is incorrect", None
        if neighbourId not in neighbourIds:
            return "The packet received not from the neighbour", None

        payload = data[8:]
        routes = {}
        for i in range(40, len(payload) + 1, 40):
            entry = payload[i-40:i]
            _, _, destId, _, _, metric = struct.unpack('>2i4q', entry)
            if metric > 16 or metric < 1:
                return "Metric of a route is out of range", None
            routes[destId] = metric

        return None, (neighbourId, routes)
