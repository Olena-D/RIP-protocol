###########################################################################
#                                                                         #
# "Daemon" Class is responsible for organization and coordination of      #
# other components of the program. All communication between peer         #
# routers is controlled by that class.                                    #
#                                                                         #
###########################################################################

import socket
import select
import time

import timer

from translator import Translator
from routing_table import RoutingTable
from sender import Sender


class Daemon(object):
    def __init__(self, cfg):
        self.__ports = cfg.getInputPorts()
        self.__neighbourIds = list(
            map(lambda x: x["neighbourId"], cfg.getOutputs()))
        self.__neighboursInfo = dict(
            map(lambda x: (x["neighbourId"], x["metric"]), cfg.getOutputs()))

        self.__timer = timer.Timer(cfg.getPeriod())
        self.__table = RoutingTable(
            cfg.getRouterId(), self.__timer, self.__neighboursInfo)

        self.__translator = Translator()
        self.__sender = Sender(cfg, self.__translator)

    def run(self):
        channels = list(map(self.__createSocket, self.__ports))
        self.__periodicUpdate()

        while True:
            start = time.monotonic()
            (readable, _, _) = select.select(
                channels, [], [], self.__timer.getTimeout())

            taskList = self.__timer.elapse(time.monotonic() - start)
            self.__perform(taskList)

            for sock in readable:
                data, _ = sock.recvfrom(self.__translator.getBufferSize())
                err, message = self.__translator.unpack(
                    data, self.__neighbourIds)

                if err is not None:
                    print(err)
                    continue

                self.__table.update(*message)
                self.__table.print()

    def __createSocket(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', port))
        sock.setblocking(False)
        return sock

    def __periodicUpdate(self):
        self.__timer.addTask("update")
        self.__sender.send(self.__table.getRecords())

    def __perform(self, taskList):
        for task in taskList:
            if task.action == "update":
                self.__periodicUpdate()
                continue
            if task.action == "timeout":
                self.__table.routeDown(task.routerId)
                continue
            if task.action == "garbage":
                self.__table.removeRoute(task.routerId)
