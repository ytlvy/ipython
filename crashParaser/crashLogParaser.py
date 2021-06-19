#!/usr/bin/python3

import sys
import os
import re
import hashlib
import codecs
import json
import ntpath

class crashInfo:
    def __init__(self):
        self.lines      = []
        self.identifiers = []
        self.count      = 0
        self.reason     = ""
        self.loadAdress = ""
        self.version    = ""
        self.kwAddress  = []
        self.symbolic   = ""
        self.devicetype = "arm64"
        self.rawdata    = ""

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
        self.otherInfo = ""
        self.lineCount = 0
        self.versionStatistic = {}

    def parse(self):
        fileHandle = open(self._filepath, mode='r')
        
        for line in fileHandle.readlines():
            self.lineCount += 1
            self.parseLine(line)

        sortedlist = sorted(self.crashs, key = lambda name: self.crashs[name].count, reverse=True)
        # sortedDic = sorted(self.crashs.values(), key=operator.attrgetter('count'))
        # print(sortedlist)
        self.symbolic(sortedlist)
        self.otherStatistic(sortedlist)
        self.output(sortedlist)
        fileHandle.close()

    def parseLine(self, line):
        info = crashInfo()
        info.rawdata = line
        info.version = self.parseVersion(line)

        if info.version in self.versionStatistic:
            self.versionStatistic[info.version] += 1
        else:
            self.versionStatistic[info.version] = 1

        info.reason  = self.parseException(line)
        info.loadAdress = self.parseLoadAddress(line)
        self.parseStack(line, info)
        self.refreshStatics(info)
    
    def parseStack(self, line, info):

        frames = self.parseFrames(line)
        # if(len(frames) < 1):
        #     print(" 分析frame 失败:" + line)

        identifiers = []
        kwidentifiers = []
        for frame in frames:
            info.lines.append(frame)
            identifier = self.parseFrameidentifier(frame)
            # kwidentifier = self.parseFrameKwidentifier(frame)

            # print("identifier:" + identifier)
            identifiers.append(identifier)
            # kwidentifiers.append(kwidentifier)

            kwaddress = self.parseKWAddress(frame)
            if(len(kwaddress) > 0):
                if len(kwaddress) < 16:
                    info.devicetype = "armv7"
                # print("kwaddress:" + kwaddress)
                info.kwAddress.append(kwaddress)
        
        if len(kwidentifiers) > 0:
            info.identifiers = kwidentifiers
        else:
            info.identifiers = identifiers

    def output(self, sortedlist):
         filename = os.path.splitext(self._filepath)[0]
         filename = ntpath.basename(filename) + "_report.txt"
         with codecs.open(filename, "w+", "utf-8") as outF:

            outF.write(f'total crash:{self.lineCount}\n')
            outF.write("other statistic:\n")
            outF.write(self.otherInfo)
            outF.write(os.linesep)
            
            sortedVersion = dict(sorted(self.versionStatistic.items(), key=lambda item: item[1], reverse=True))
            outF.write(json.dumps(sortedVersion))
            outF.write(os.linesep)

            for v in sortedlist:
                crashInfo = self.crashs[v]
                outF.write("===================== crash num:%d" % (crashInfo.count))
                outF.write(os.linesep)
                outF.write("version : %s" % (crashInfo.version) )
                outF.write(os.linesep)
                outF.write("loadAdress : %s" % (crashInfo.loadAdress) )
                outF.write(os.linesep)
                outF.write("===== reason:\n")
                outF.write(crashInfo.reason)
                if len(crashInfo.symbolic) > 0:
                    outF.write("===== symbolic:\n")
                    outF.write(crashInfo.symbolic)
                outF.write(os.linesep)

                if( len(crashInfo.lines) > 0):
                    outF.write("===== stack:\n")
                    for ln in crashInfo.lines:
                        outF.write(ln)
                        outF.write(os.linesep)
                    outF.write(os.linesep)
                else:
                    outF.write("===== rawdata:\n")
                    outF.write(crashInfo.rawdata)
                    outF.write(os.linesep)


    def otherStatistic(self, sortedlist):
        otherKey = {"[__NSCFNumber length]":0, "AVPlayerItem was deallocated":0}
        for v in sortedlist:
            crashInfo = self.crashs[v]
            for k in otherKey:
                if( k in crashInfo.reason):
                    otherKey[k] += crashInfo.count

        result = json.dumps(otherKey)
        print(result)
        self.otherInfo = result
        return  result
        

    def parseVersion(self, line):
        pattern = re.compile(r'SRC:kwplayer_ip_(\d+\.\d+\.\d+)', re.I | re.S)
        rs = pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return ""
        return rs.group(1)

    def parseException(self, line):
        reason_pattern = re.compile(r'Exception Reason([^;]*)', re.I | re.S)
        rs = reason_pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return ""
        return rs.group(0)

    def parseLoadAddress(self, line):
        ld_pattern = re.compile(r'LoadAddress[^;]*(0x[A-Fa-f0-9]*)', re.I | re.S)
        rs = ld_pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return ""

        return rs.group(1)

    def parseFrames(self, line):
        pattern = re.compile(r'Callstack[^(]*\(([^\)]*)\)', re.I | re.S)
        rs = pattern.search(line)
        if rs == None or len(rs.group(1).strip()) < 1:
            return []
        
        source = rs.group(1)
        # print("==============source, %s" %(source))
        return source.split(",")

    def parseFrameidentifier(self, frame):
        pattern = re.compile(r'(\s?\t{0,}\d*\s+\S+\s*0x\w+\s+([^,]*))', re.I | re.S)
        results = re.search(pattern, frame)
        if results == None or len(results.group(1).strip()) < 1:
            print("==============frame, %s" %(frame))
            raise ValueError("行数获取失败")

        # print(results.group(2))     

        return results.group(2)
    
    def parseFrameKwidentifier(self, frame):
        pattern = re.compile(r'\s?\t{0,}\d*\s+KWPlayer\s*0x\w+\s+([^,]*)', re.I | re.S)
        results = re.search(pattern, frame)
        if results == None or len(results.group(1).strip()) < 1:
            # print("==============frame, %s" %(frame))
            return ""

        return results.group(1)
            
    def parseKWAddress(self, frame):

        address = ""
        # 分析关键s?\t{0,}\d*\s+KWPlayer\s*(0x\w+)\s+[^,]*
        pattern = re.compile(r'(s?\t{0,}\d*\s+KWPlayer\s*(0x\w+)\s+[^,]*)', re.I | re.S)
        results = re.search(pattern, frame)
        if results != None and len(results.group(1).strip()) > 0:
            address = results.group(2).strip()

        return address
    
    def symbolic(self, sortedlist):
        count = 0
        for v in sortedlist:
            info = self.crashs[v]
            if len(info.kwAddress) < 1:
                # print("kwAddress: %s" %(info.kwAddress))
                continue
            
            #symbolic
            curDic = os.getcwd() #os.path.split(os.path.realpath(__file__))[0]
            dsym_dir_path = curDic+os.path.sep+info.version+"/KWPlayer.app.dSYM/Contents/Resources/DWARF/KWPlayer"
            if not os.path.exists(dsym_dir_path):
                # print("符号版本文件夹不存在: %s" %(dsym_dir_path))
                continue

            unsymbolic = " ".join(info.kwAddress)
            commandStr = f"atos -arch {info.devicetype} -o {dsym_dir_path} -l {info.loadAdress} {unsymbolic}"
            # print("commandStr : %s" %(commandStr))
            atos_result = os.popen(commandStr).read()
            
            info.symbolic = str(atos_result)
            # print(info.symbolic)
            count += 1
            if(count > 50):
                break
    

    def refreshStatics(self, info):
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
    if filepath.startswith('.'):
        curDic = os.getcwd() #os.path.split(os.path.realpath(__file__))[0]
        # print(f'curdir: {curDic}')
        filepath = curDic + os.path.sep+filepath[2:]
        # print(f'filepath: {filepath}')

    parser = CrashLogParaser(filepath)
    parser.parse()
