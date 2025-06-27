###--Routing Table--###

import copy

class Route(object):
    def __init__(self, route, neighbour, metric):
        self.__inf = 16
        self.route = route
        self.neighbour = neighbour
        self.metric = metric
        self.flag = 0

    def update(self, neighbour, totalCost, timer):
        if totalCost >= self.metric and neighbour != self.neighbour:
            return

        if self.flag == 1 and totalCost == self.__inf:
            return

        if totalCost == self.__inf and self.flag == 0:
            timer.addTask("garbage", self.route)
            timer.addTask("trigger")
            self.metric = self.__inf
            self.flag = 1
            return

        self.metric = totalCost
        self.neighbour = neighbour
        self.flag = 0
        timer.addTask("timeout", self.route)


class RoutingTable(object):
    def __init__(self, routerId, timer, neighbourInfo):
        self.__routerId = routerId
        self.__table = {}
        self.__inf = 16
        self.__neighbourInfo = neighbourInfo
        self.__timer = timer

    def getRecords(self):
        return copy.deepcopy(self.__table)

    def update(self, neighbour, routes):
        self.__addOrUpdateRoute(neighbour, neighbour,
                                self.__neighbourInfo[neighbour])

        for route, cost in routes.items():
            if route == self.__routerId:
                continue

            totalCost = min(self.__table[neighbour].metric + cost, self.__inf)
            self.__addOrUpdateRoute(route, neighbour, totalCost)

    def routeDown(self, route):
        record = self.__table[route]
        record.update(record.neighbour, self.__inf, self.__timer)

    def removeRoute(self, route):
        self.__table.pop(route)

    def print(self):
        print("\nRIP router-{} Routing Table".format(self.__routerId))
        print("============================================================")
        print("Destination  Next hop    Metric  Timer-Type   Duration")
        print("============================================================")

        for _, record in sorted(self.__table.items()):
            timerType, duration = self.__timer.getTime(record.route)
            print("{:<13}{:<12}{:<8}{:<13}{:<8}".format(
                record.route, record.neighbour, record.metric, timerType, duration))
            print("------------------------------------------------------------")

    def __addOrUpdateRoute(self, route, neighbour, cost):
        if route in self.__table:
            self.__table[route].update(neighbour, cost, self.__timer)
            return

        if cost < self.__inf:
            newRoute = Route(route, neighbour, cost)
            self.__table[route] = newRoute
            self.__timer.addTask("timeout", newRoute.route)
