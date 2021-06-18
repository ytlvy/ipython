'''
Author: Y.t
Date: 2021-06-18 17:18:24
LastEditors: Y.t
LastEditTime: 2021-06-18 18:02:01
Description: 
'''

import sys
import os
import datetime
import urllib.request
from dateutil import parser

class LogFecther:
    def __init__(self, begin_date_str, days):
        self.begin_date_str = begin_date_str
        self.days = int(days)

    def doFetch(self):
        begin_date = parser.parse(self.begin_date_str)
        next_date = begin_date + datetime.timedelta(days=1)
        self.fetchUrl(begin_date)

        if self.days > 1:
            for i in range(1, self.days):
                begin_date += datetime.timedelta(days=1)
                self.fetchUrl(begin_date)

    def fetchUrl(self, date):
        url = "http://mobilefhtj.kuwo.cn/iphoneErrorLog/{}_error_log".format(date.strftime('%Y-%m-%d'))
        urllib.request.urlretrieve(url, date.strftime('%Y-%m-%d')+".txt")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("请输入日志文件开始日期 - 天数")

    begin_date_str = filepath = sys.argv[1]
    count = 1
    if len(sys.argv) == 3:
        count = sys.argv[2]
    
    fetcher = LogFecther(begin_date_str, count)
    fetcher.doFetch()

