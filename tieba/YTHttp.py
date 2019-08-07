#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import sys
import socket

from YTBase import YTBase


class YTHttp(YTBase):
    '''
    获取url内容
    '''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) '
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/46.0.2490.80 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;'
        + 'q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6',
        'Connection': 'keep-alive'
    }

    def __init__(self, isjson=False):
        """
        初始化属性
        :param is_json: 返回结果是否为json
        """

        super(YTHttp, self).__init__()

        self.timeout = 120.0
        self._isJson = isjson

    def request(self, url, method='get', values=False):
        """
        获取url内容
        :param url:网络地址
        :param method 方法 'get' 'post'
        :param values: 数据 dict
        :rtype : string
        """
        self.log("get url: {0} content start\n".format(url))

        # post请求数据整理
        if method == 'get':
            req = urllib.request.Request(url, headers=YTHttp.headers)

        elif method == 'post':
            pdata = urllib.urlencode(values) if values else ''
            req = urllib.request.Request(url, data=pdata, headers=self.headers)

        else:
            self.log('unknown http protocol')
            raise ValueError('unknown http protocol')

        try:
            response = urllib.request.urlopen(req, timeout=self.timeout)
            data = response.read()
        except urllib.request.URLError as e:
            self.log("get url: {0} error".format(url))

            if hasattr(e, 'code'):
                msg = "urlopen error code:" + str(e.code)
            else:
                msg = ""
            msg += "reason:" + e.read() if hasattr(e, 'reason') else ''
            self.log(msg)

            return ''
        except socket.timeout as e:
            self.log("get url: {0} error time out\n".format(url))
            return ''

        else:

            self.log("get url: {0} content done\n".format(url))

            # 解压
            if 'content-encoding' in response.headers:
                import StringIO
                import gzip

                fileobj = StringIO.StringIO
                fileobj.write(data)
                fileobj.seek(0)
                gzip_file = gzip.GzipFile(fileobj=fileobj)
                data = gzip_file.read()

            return self._decode(data)

    def _decode(self, raw_data):
        """
        将获取的内容解码为本地数据
        :param raw_data: 获取的原始数据
        :rtype string
        """
        raw_data = raw_data.decode('utf-8')
        if self._isJson:
            import json
            raw_data = json.loads(raw_data)

        return raw_data

if __name__ == '__main__':
    sys.getfilesystemencoding()
