#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*-encoding=utf-8-*-

import threading
import time
import queue

from YTBase import YTBase


class CleanOutpuSet(set):
    def __str__(self):
        return ", ".join(x for x in self)


class YThread(threading.Thread, YTBase):

    remaining = CleanOutpuSet()
    queue = queue.Queue()

    def __init__(self, func, args, name=""):
        # super(YThread, self).__init__();
        threading.Thread.__init__(self)
        YTBase.__init__(self)

        self.name = name
        self.func = func
        self.args = args

    def result(self):
        """
        获取结算结果s
        :return:
        """
        return self.res

    def run(self):
        """

        """
        tname = threading.currentThread().name
        YThread.remaining.add(tname)
        self.log("starting {0} at: {1} \n".format(tname, time.ctime()))

        self.res = self.func(*self.args)

        YThread.remaining.remove(tname)
        self.log("{0} finished at: {1}\n".format(tname, time.ctime()))
        self.log("remaining: {0} \n".format(YThread.remaining or None))
