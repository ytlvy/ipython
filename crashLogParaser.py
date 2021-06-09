#!/usr/bin/python3

import sys
import os
import re
import hashlib
import codecs

class crashInfo:
    def __init__(self):
        self.source     = ""
        self.lines      = []
        self.identifiers = []
        self.count      = 0
        self.reason     = ""
        self.loadAdress = ""
        self.version    = ""

    def identifier(self):
        content = str("-".join(self.identifiers)).encode('utf-8')
        return hashlib.md5(content).hexdigest()

class CrashLogParaser():
    """
    crash log paraser
    """

    def __init__(self, path):
        self._filepath = path
        self.crashs = {}

    def parse(self):
        fileHandle = open(self._filepath, mode='r')
        for line in fileHandle.readlines():
            self.parseLine(line)

        sortedlist = sorted(self.crashs, key = lambda name: self.crashs[name].count, reverse=True)
        # sortedDic = sorted(self.crashs.values(), key=operator.attrgetter('count'))
        # print(sortedlist)

        with codecs.open("crashReport.txt", "w+", "utf-8") as outF:
            for v in sortedlist:
                crashInfo = self.crashs[v]
                outF.write("===================== crash num:%d" % (crashInfo.count))
                outF.write(os.linesep)
                outF.write("version : %s" % (crashInfo.version) )
                outF.write(os.linesep)
                outF.write("loadAdress : %s" % (crashInfo.loadAdress) )
                outF.write(os.linesep)
                outF.write(crashInfo.reason)
                outF.write(os.linesep)

                for ln in crashInfo.lines:
                    outF.write(ln)
                    outF.write(os.linesep)
                outF.write(os.linesep)

        fileHandle.close()

    def parseLine(self, line):
        info = crashInfo()
        from_pattern = re.compile(r'SRC:([^|]+)', re.I | re.S)
        rs = from_pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return
        info.version = rs.group(1)

        reason_pattern = re.compile(r'Exception Reason([^;]*)', re.I | re.S)
        rs = reason_pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return
        info.reason = rs.group(0)

        ld_pattern = re.compile(r'LoadAddress[^;]*(0x[A-Fa-f0-9]*)', re.I | re.S)
        rs = ld_pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return
        info.loadAdress = rs.group(1)

        pattern = re.compile(r'Callstack \$ \(([^\)]*)\)', re.I | re.S)
        rs = pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return
        
        info.source = rs.group(1)

        # print("==============source, %s" %(info.source))

        clines = info.source.split(",")

        for cline in clines:
            pattern = re.compile(r'(\s?\t{0,}\d*\s+\S+\s*0x\w+\s+([^,]*))', re.I | re.S)
            results = re.search(pattern, cline)
            if results == None or len(results.group(1).strip()) < 1:
                print("==============cline, %s" %(cline))
                raise ValueError("行数获取失败")

            # print(results.group(2))     

            info.identifiers.append(results.group(2))
            info.lines.append(results.group(1))
            

        identifier = info.identifier()

        # print("========== lines %s", info.identifiers)
        # print("========== identifier %s", identifier)
        if identifier in self.crashs:
            crashinfo = self.crashs[identifier]
            crashinfo.count = crashinfo.count + 1
            # print("========== old crash %s count: %d", identifier, crashinfo.count)
        else:
            # print("========== new crash %s", identifier)
            self.crashs[identifier] = info

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("请输入日志文件")

    filepath = sys.argv[1]
    if filepath.startswith('~'):
        filepath = os.path.expanduser(filepath)
    parser = CrashLogParaser(filepath)
    parser.parse()
