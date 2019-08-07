#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import os
import re
import time
import codecs
import collections

from atexit import register
from YThread import YThread
from YTBase import YTBase
from YTHttp import YTHttp


class YTieba(YTBase):
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

        super(YTieba, self).__init__()

        self.ckdir(path)    # 检测并创建目录
        self._path = path
        self._url = url

        self._page_pool = {}
        self._http = YTHttp()

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
        con = self._http.request(url)

        patternstr = r'<li class="l_reply_num"[^>]*>[^<]*<span[^>]*>(\d+)'\
            r'</span>[^<]*</li>'
        pattern = re.compile(patternstr, re.I | re.S)
        rs = pattern.search(con)

        return int(rs.group(1)) if rs is not None else 1

    def page_urls(self, page_num):
        """
        生成所有页面链接
        :param page_num: 总页数
        :rtype: list
        """
        urls = []
        for x in list(range(1, page_num + 1)):
            if re.search(r'\?', self._url):
                urls.append("{0:s}&pn={1:d}".format(self._url, x))
            else:
                urls.append("{0:s}?pn={1:d}".format(self._url, x))

        return urls

    def retrieve_image(self, con):
        """
        图片处理
        :param con: 抓取的html内容
        """
        pattern = re.compile(r'<img[^>]*src="([^"]*)"[^>]*>', re.I)
        for img in pattern.finditer(con):

            if re.search(b"(?:png|gif)$", img.group(1)):    # png gif 图片不生成
                continue

            imgurl = img.group(1)

            filename = self._path + imgurl.split("/")[-1]
            filepath = "{0}/{1}".format(self._path, filename)

            if not os.path.exists(filepath):
                urllib.urlretrieve(imgurl, filepath, None)

                self.log("generate img: " + filepath)

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
        # return con.decode(sys.getfilesystemencoding())

    def parse_html(self, url, num):
        """
        页面分析处理

        :param url: 页面链接
        """

        content = self._http.request(url)           # get url content

        patternstr = r'<cc><div[^>]*class="d_post_content '\
            r'j_d_post_content"[^>]*>.*?</div></cc>'
        pattern = re.compile(patternstr, re.I | re.S)
        for line in pattern.finditer(content):
            self.retrieveImg(line.group())
            if num in self._page_pool:
                self._page_pool[num] = self._page_pool[num] + "\n"
                + self.stripTags(line.group())
            else:

                self._page_pool[num] = self.stripTags(line.group())

    def thread_callback(self):
        """
        write page pool to file
        """

        self.log("******** BEGIN WRIETE FILE ********")

        file = self._path + "/index.txt"
        infile = codecs.open(file, 'w', 'utf-8')

        order_dict = collections.OrderedDict(sorted(self._page_pool.items(),
                                             key=lambda x: x[0]))
        for line in order_dict:
            infile.write(order_dict[line])

        self._page_pool = False

        self.log("******** ALL DONE ********")

    def main(self):
        """
        分析html页面
        :param url: 页面内容
        """

        # 生成所有页面链接
        page_num = self.page_num()        # get page num
        pages = self.genPageUrls(page_num)

        # 多线程抓取处理页面
        for i in range(page_num):
            YThread(self.parseHtml, (pages[i], i + 1), i + 1).start()
            time.sleep(0.5)

        register(self.thread_callback)


if __name__ == '__main__':
    url = r'http://tieba.baidu.com/p/2251498697'
    # url = r'http://tieba.baidu.com/p/2326623142?see_lz=1'
    path = '2000'
    print("input url:")
    url = input()

    print("path:")
    path = input()

    tieba = YTieba(path, url)
    tieba.main()
