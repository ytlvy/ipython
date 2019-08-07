#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -*- encoding=utf-8 -*-

from atexit import register
from random import randrange
import threading
import time


class CleanOutputSet(set):
    def __str__(self):
        return ", ".join(x for x in self)


class Candy():

    def __init__(self, max):
        self._lock = threading.Lock()
        self._max = max
        self._candyTray = threading.BoundedSemaphore(self._max)

    def _refill(self):
        self._lock.acquire()
        print("Refilling candy...")

        try:
            self._candyTray.release()
        except ValueError:
            print("full, skipping")
        else:
            print("OK")
        self._lock.release()

    def _buy(self):
        self._lock.acquire()
        print "Buying candy...",
        if self._candyTray.acquire(False):
            print "OK"
        else:
            print "empty, skipping"
        self._lock.release()

    def producer(self, loops):
        for i in xrange(loops):
            self._refill()
            time.sleep(randrange(3))

    def consumer(self, loops):
        for i in xrange(loops):
            self._buy()
            time.sleep((randrange(3)))

    def _main(self):
        print "starting at:", time.ctime()
        nloops = randrange(2, 6)
        print "THE CANDY MACHINE (full with {0:d} bars)".format(self._max)

        threading.Thread(target=self.consumer, args=(randrange(nloops, nloops +
                         self._max + 2), )).start()
        threading.Thread(target=self.producer, args=(nloops, )).start()


@register
def _atexit():
    print "ALL DONE... at:", time.ctime()

if __name__ == "__main__":
    candy = Candy(5)
    candy._main()
