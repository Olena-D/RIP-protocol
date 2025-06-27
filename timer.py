# ============================= Regarding timer ==========================
""" The basic idea is each timer that need to be setted is represent as 
an object of class Task. Each Task has a remaining time and action that 
should be perform when the time is up. A collection of task objects is 
store and managed by a timer class object. There is no actual 
functionality for measuring time in these two classes. That should be 
done in the main function using the timeout of the select system call 
in combination with the time module An important assumption that has 
been made here is that the time performing other actions other than 
waiting for select system call to return or timeout is negligible"""
# ========================================================================
import random


class Task():

    def __init__(self, duration, action, routerId):
        self.duration = duration
        self.action = action
        self.routerId = routerId

    def elapse(self, duration):
        self.duration -= duration

    def isDue(self):
        return self.duration <= 0


class Timer():

    def __init__(self, period):
        self.__taskList = []
        self.__update = period
        self.__garbage = period * 4
        self.__timeout = period * 6

    def addTask(self, task, routerId=-1):
        if task == "update":
            self.remove("update", routerId)
            self.__taskList.append(
                Task(self.__update * random.uniform(0.8, 1.2), "update", routerId))

        if task == "trigger":
            self.remove("update", routerId)
            self.__taskList.append(Task(0, "update", routerId))

        if task == "garbage":
            self.remove("timeout", routerId)
            if self.checkDup("garbage", routerId):
                return

            self.__taskList.append(
                Task(self.__garbage * random.uniform(0.8, 1.2), "garbage", routerId))

        if task == "timeout":
            self.remove("garbage", routerId)
            self.remove("timeout", routerId)
            self.__taskList.append(
                Task(self.__timeout * random.uniform(0.8, 1.2), "timeout", routerId))

    def remove(self, action, routerId):
        """for a given destination, remove the specific type of timer"""
        for task in self.__taskList:
            if task.action == action and task.routerId == routerId:
                self.__taskList.remove(task)

    def checkDup(self, action, routerId):
        """return true if the timer of the given type to the destination already exist"""
        for task in self.__taskList:
            if task.action == action and task.routerId == routerId:
                return True
        return False

    def elapse(self, duration):
        """move the timer forward by the given duration
        return a list of all task that needed to be perform"""
        actionList = []
        for task in self.__taskList:
            task.elapse(duration)
            if task.isDue():
                actionList.append(task)
                self.__taskList.remove(task)
        return actionList

    def getTime(self, destination):
        """for the given destination, return the timer status of the route (timeout/grabage)
        and the duration of said timer as a pair of string and integer"""
        for task in self.__taskList:
            if task.routerId == destination:
                return task.action, int(task.duration)

    def getTimeout(self):
        """return duration of the task with the least duration remaining
        use this as the timeout duration for select system call"""
        return min([task.duration for task in self.__taskList])
