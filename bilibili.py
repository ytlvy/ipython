#!/usr/bin/env python3
import re
import os
import hashlib
import requests
import xmlrpc.client

# key & secret from 'you-get'
key = '85eb6835b0a1034e'
secret = '2ad42749773c441109bdc0191257a664'
user_agent = ("Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0.2) "
              "Gecko/20100101 Firefox/6.0.2 Fengfan/1.0")
headers = {"User-Agent": user_agent,
           # fake ip in China
           "X-Forwarded-For": "220.181.111.81",
           "Client-IP": "220.181.111.81"}
server = xmlrpc.client.ServerProxy('http://127.0.0.1:6800/rpc')
path = os.path.expanduser("~") + "/Movies/Bilibili/"


def get_cid_title(av, part=1):
    ''' get cid & title '''
    global headers
    url = "http://www.bilibili.com/video/" + av
    if part != 1:
        url += '/index_{}.html'.format(part)
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    cid = re.search(r"cid=(\d+)", r.text).group(1)
    title = re.search(r'h1 title="([^"]*)"', r.text).group(1)
    return (cid, title)


def make_output_dir(title):
    ''' make the output dir '''
    global path
    outdir = path + title.replace('/', '')
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    return outdir


def download_urls(cid):
    ''' get video urls '''
    global key, secret
    # gen the sign
    param = "appkey={}&otype=json&cid={}&quality=4&type=flv{}".format(
        key, cid, secret)
    sign = hashlib.md5(param.encode('utf-8')).hexdigest()
    # query the video files
    requrl = ("http://interface.bilibili.com/playurl?appkey={}&otype=json"
              "&cid={}&quality=4&type=flv&sign={}").format(key, cid, sign)
    json = requests.get(requrl, headers=headers).json()
    # pprint(json)
    return json['durl']


def call_aria2_rpc(url, outdir):
    ''' call aria2 rpc '''
    global server
    return server.aria2.addUri([url], dict(dir=outdir))


def get_comments(cid, outdir):
    with open('{}/{}.xml'.format(outdir, cid), 'w') as f:
        cmts = "http://comment.bilibili.com/{}.xml".format(cid)
        r = requests.get(cmts)
        r.encoding = 'utf-8'
        f.write(r.text)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Bilibili to aria2c.")
    parser.add_argument('av', help="avXXX")
    parser.add_argument('part', nargs='?', type=int, default=1,
                        help="2 or 3, 4 ...")
    args = parser.parse_args()
    av = args.av
    if not av.startswith('av'):
        av = av[av.index('av'):].rstrip('/')
    cid, title = get_cid_title(av, args.part)
    print("cid: {}\ntitle: {}".format(cid, title))
    # the download path
    outdir = make_output_dir(title)
    print("dir: {}".format(outdir))
    durl = download_urls(cid)
    # pprint(durl)#; return
    if 'url' in durl:
        durl = [durl]
    for u in durl:
        print("url: {}".format(u['url']))
        call_aria2_rpc(u['url'], outdir.encode('utf-8'))
    # the comments
    get_comments(cid, outdir)

if __name__ == '__main__':
    main()
