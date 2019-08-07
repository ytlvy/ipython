#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import time
import sys
import urllib
import socket
# import codecs
# import collections
import signal

from atexit import register
from multiprocessing import Pool

from YThread import YThread
from YTBase import YTBase
from YTHttp import YTHttp


import requests
requests.adapters.DEFAULT_RETRIES = 5


class YT177(YTBase):
    """
    百度贴吧链接抓取脚本
    本脚本只抓取信息主体部分，并提取纯文本 和 图片

    @author: Gyj 2013-5-25
    """

    def __init__(self, path, url):
        """
        初始化多线程
        :param path: 存储路径
        :param url: url地址
        """

        super(YT177, self).__init__()

        self.ckdir(path)    # 检测并创建目录
        self._path = path
        self._url = url

        self._page_pool = {}

    def ckdir(self, path):
        """
        检测，并生成目录
        :param path: 目录
        """

        path = path.strip()         # 去除空格
        path = path.rstrip("\\")    # 去除末尾分隔符

        # 创建目录操作函数
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as why:
                self.log(why)
                raise

    def page_num(self):
        """
        获取链接总页数
        :rtype : int
        """

        response = requests.get(url)
        con = response.text

        # print("网页内容:" + con)
        # sys.stdout.flush()

        # 抓取页面部分
        pattern = re.compile(r'<div class="wp-pagenavi">(.*?)</div>',
                             re.I | re.S)
        rs = pattern.search(con)

        if len(rs.groups()) == 0:
            raise ValueError('分析页码部分错误')

        pattern = re.compile(r'<a href="[^"]+/(\d+)"[^>]*>', re.I | re.S)
        results = re.findall(pattern, rs.group(1))

        if len(results) == 0:
            raise ValueError("页码数组分析错误")

        results = [int(i) for i in results]
        results.sort()

        return int(results.pop()) if rs is not None else 1

    def page_urls(self, page_num):
        """
        生成所有页面链接
        :param page_num: 总页数
        :rtype: list
        """

        urls = []

        # pattern = re.compile(r'\-(\d+)\.', re.I)
        for x in list(range(1, page_num + 1)):
            # urls.append(re.sub(pattern, "-{0}.".format(x), self._url))
            urls.append("{0:s}/{1:d}".format(self._url, x))
        return urls

    def parse_html(self, url, num):
        """
        页面分析处理
        :param url: 页面链接
        """

        print("开始分析页面: " + url)
        sys.stdout.flush()

        response = requests.get(url)
        content = response.text           # get url content

        # print("图片网页内容: " + content)

        pattern = re.compile(r'<p><img[^>]*></p>', re.I | re.S)

        image_index = 0
        for line in pattern.finditer(content):
            image_index += 1

            self.retrieve_image(line.group(), num, image_index)

    def retrieve_image(self, con, page, index):
        """
        图片处理
        :param con: 抓取的html内容
        """
        pattern = re.compile(r'<img[^>]*src="([^"]*)"[^>]*>', re.I)

        # print("开始分析图片链接:" + con)

        for img in pattern.finditer(con):

            if re.search(r"(?:png|gif)$", img.group(1)):    # png gif 图片不生成
                continue

            imgurl = img.group(1)
            print("图片链接: " + imgurl)
            sys.stdout.flush()

            filename, file_extension = os.path.splitext(imgurl)
            filepath = "{0}/{1:03d}{2:03d}{3}".format(self._path, page, index,
                                                      file_extension)
            if not os.path.exists(filepath):
                self.log("generate img: " + filepath + "\n")
                self.download(imgurl, filepath)

    def download(self, url, path):
        """
        下载图片
        """

        print("开始图片下载: " + url)
        sys.stdout.flush()

        try:
            img = requests.get(url, headers=YTHttp.headers, timeout=10,
                               allow_redirects=True)

        except requests.exceptions.ConnectionError as e:

            print("ConnectionError:" + e.args[0].reason.message + "\n")
            sys.stdout.flush()

        except requests.exceptions.Timeout:
            print("下载图片超时:" + url + "\n")
            sys.stdout.flush()
        else:
            with open(path, 'wb') as f:  # 图片wb模式写入 binary
                f.write(img.content)

    def download_image(self, url, path):

        print("开始图片下载: " + url)

        req = urllib.request.Request(url, headers=YTHttp.headers)
        u = urllib.request.urlopen(req, timeout=120)
        h = u.info()
        total_size = int(h["Content-Length"])

        print("Downloading %s bytes..." % total_size)
        sys.stdout.flush()

        fp = open(path, 'wb')

        block_size = 8192
        count = 0
        percent = 0
        while True:
            try:
                chunk = u.read(block_size)
                if not chunk:
                    break
                fp.write(chunk)
                count += 1
                if total_size > 0:
                    percent = int(count * block_size * 100 / total_size)
                    if percent > 100:
                        percent = 100
                    print("%2d%%" % percent)
                    if percent >= 100:
                        print("下载完毕.")

            except socket.error as socketerror:
                print("Error: ", socketerror)

        fp.flush()
        fp.close()

        if percent < 100:
            try:
                os.remove(path)
            except OSError:
                pass

        if not total_size:
            print("download error")

    def strip_tags(self, con):
        """
        删除html标签
        :param con: 抓取的html内容
        :rtype string
        """
        con = re.compile(b'(</?br>)+').sub(b'\n', con)      # delete blank
        con = re.compile(b'(\n\r?)+').sub(b'\n', con)       # delete blank
        con = re.compile(b'</?[^>]*>').sub('', con)         # delete html tag

        return con

    def main(self):
        """
        分析html页面
        :param url: 页面内容
        """

        # 生成所有页面链接
        page_num = self.page_num()
        pages = self.genPageUrls(page_num)

        # 多线程抓取处理页面
        for i in range(page_num):
            YThread(self.parseHtml, (pages[i], i + 1), i + 1).start()
            time.sleep(1)

        register(self.writeDicToFile)


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def myfunction(url, num):
    dl = YT177(path, url)
    dl.parse_html(url, num)

if __name__ == '__main__':

    url = r'http://www.177pic.info/html/2014/01/32849.html'
    path = '/Users/zyn/Comic/111'

    dl = YT177(path, url)
    # dl.download(r"http://img.177pic.info/uploads/2014/01a/01.jpg", "111.jpg")
    # exit()

    # 生成所有页面链接
    page_num = dl.page_num()
    pages = dl.page_urls(page_num)

    if True:
        myfunction(pages[0], 1)
    else:
        pool = Pool(10, init_worker)
        for i in range(page_num):
            pool.apply_async(myfunction, args=(pages[i], i + 1, ))

        try:
            print("Waiting 10 seconds")
            sys.stdout.flush()
            time.sleep(10)

        except KeyboardInterrupt:
            print("Caught KeyboardInterrupt, terminating workers")
            pool.terminate()
            pool.join()

        else:
            print("Quitting normally")
            pool.close()
            pool.join()
