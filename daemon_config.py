###########################################################################
#                                                                         #
# "DaemonConfig" Class is responsible for getting information out from    #
# the configuration file.                                                 #
#                                                                         #
# Instance variables have the following formats:                          #
#                                                                         #
# 1. self.__routerId and self.__period are integers                       #
# 2. self.__inputPorts is a list of integers ex: [6061, 6062]             #
# 3. self.__outputs is a list of dictionaries                             #
#       ex: [{"port": 6061, "metric": 1, "routerId": 1}]                  #
#                                                                         #
###########################################################################

import configparser
import sys


class DaemonConfig(object):
    def __init__(self, filename):
        self.__filename = filename
        self.__routerId = 0
        self.__period = 0
        self.__inputPorts = []
        self.__outputs = []

    def load(self):
        config = configparser.ConfigParser()
        config.read(self.__filename)

        self.__routerId = config.getint('routerd', 'router-id')
        self.__period = config.getint('routerd', 'period')
        self.__inputPorts = list(
            map(int, (config.get('routerd', 'input-ports').split(', '))))
        self.__outputData = config.get('routerd', 'outputs').split(', ')
        self.__outputs = self.__defineOutputs()

        error = self.__validate()
        return error

    def getRouterId(self):
        return self.__routerId

    def getPeriod(self):
        return self.__period

    def getInputPorts(self):
        return self.__inputPorts[:]

    def getOutputs(self):
        return self.__outputs[:]

    def __defineOutputs(self):
        values = []
        for output in self.__outputData:
            item = list(map(int, output.split('-')))
            values.append(
                {"port": item[0], "metric": item[1], "neighbourId": item[2]})
        return values

    def __validate(self):
        errors = ""

        if self.__routerId < 1 or self.__routerId > 64000:
            errors += "Invalid router id.\nRouter id must be between 1 and 64,000\n"

        if self.__period < 1:
            errors += "Period for timer can not be negative.\n"

        for port in self.__inputPorts:
            if port < 1024 or port > 64000:
                errors += "Invalid input ports.\nInput port number must be between 1024 and 64,000\n"
                break

        if len(self.__inputPorts) != len(set(self.__inputPorts)):
            errors += "Duplicate input port detected\n"

        for output in self.__outputs:
            if output["port"] < 1024 or output["port"] > 64000 or output["port"] in self.__inputPorts:
                errors += "Invalid output ports.\nOutput port number must be between 1024 and 64,000\n"
                break

        for output in self.__outputs:
            if output["metric"] < 1 or output["metric"] > 15:
                errors += "Invalid metric value. \nMetric must be between 1 and 15\n"
                break

        return errors
