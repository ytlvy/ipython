#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import threading

lock = threading.Lock()


class YTBase(object):
    """
    基础类
    包括错误级别开启、
    """

    def __init__(self):
        """
        初始化苏醒
        """
        self._debug = False

    @property
    def debug(self):
        """
        开启调试状态
        """
        return self._debug

    @debug.setter
    def debug(self, value):
        """
        关闭调试状态
        """
        self._debug = value

    def log(self, msg):
        with lock:
            log_handler = codecs.open('log.txt', 'a+', 'utf-8')
            log_handler.write(msg)

            if(self._debug):
                print(msg)
