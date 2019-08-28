#!/usr/local/bin/python3

import os
import re
import subprocess


class YTLibFix():
    """
    fix xcode custom library compile path
    """

    def __str__(self):
        return "fix xcode custom library debug source path bug"

    def __init__(self, libs):
        self._lib, self._cpath = libs

    def relative_path_for_item(self, libname):
        """
        find libName's relative path from workspace
        """

        if len(libname) == 0:
            return ""

        findcmd = 'find . -name "' + libname + '"'
        # print("findcmd : " + findcmd)

        outputs = self.sys_command_out(findcmd)

        if len(outputs) == 0:
            raise

        return outputs[0]

    def sys_command_out(self, command):

        out = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (stdout, stderr) = out.communicate()
        filelist = stdout.decode().split()
        return filelist

    def longest_substring(self, string1, string2):
        answer = ""
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            match = ""
            for j in range(len2):
                if (i + j < len1 and string1[i + j] == string2[j]):
                    match += string2[j]
                else:
                    if (len(match) > len(answer)):
                        answer = match
                    match = ""
        return answer

    def longest_end_subpath(self, abs_path, relative_path):
        len1, len2 = len(abs_path), len(relative_path)
        answer = ""
        for j in range(len2):
            match = ""
            if(abs_path[len1 - 1] == relative_path[j]):
                for k, l in zip(range(len1 - 1, len1 - 1 - j - 1, -1),
                                range(j, -1, -1)):
                    if(abs_path[k] != relative_path[l]):
                        match = ""
                        break
                    else:
                        match = relative_path[l:j + 1]
            if (len(match) > len(answer)):
                answer = match

        return answer

    def reverse_path(self, path):

        apath = path
        if path[0:1] == os.sep:
            apath = path[1:]
        coms = apath.split(os.sep)
        coms.reverse()

        reverse_path = os.sep + os.sep.join(coms)
        print("origin path : %s  reverse path : %s" % (path, reverse_path))

        return reverse_path

    def compile_workspace(self, compile_path, relative_path):

        # reverse_path = self.reverse_path(compile_path)
        # common_path = os.path.commonpath((relative_path[1:], reverse_path))

        # rcommon_path = self.reverse_path(common_path)
        if len(self._cpath) == 0:
            self._cpath = self.longest_end_subpath(compile_path,
                                                   relative_path[1:])
        # print("common path : %s" % (self._cpath))

        lib_workspace = compile_path[0:-len(self._cpath)]

        # print("lib_workspace :" + lib_workspace)

        return lib_workspace

    def compile_source_path(self, rpath):
        """
        get debug source path
        """

        command = 'dwarfdump ' + rpath + '|grep -m1 "AT_comp_dir"'
        # print("parse command: " + command)
        outputs = self.sys_command_out(command)

        if(len(outputs) < 2):
            return ""

        pattern = re.compile(r'\("(.*?)"\)',
                             re.I | re.S)
        rs = pattern.findall(outputs[1])
        if len(rs) == 0:
            raise ValueError('extrack compile path error')

        return rs[0]

    def main(self):

        libname = self._lib

        # 相对路径
        rpath = self.relative_path_for_item(libname)
        # print("current libName: %s relative path: %s" % (libname, rpath))

        if len(rpath) < 1:
            return
        compile_path = self.compile_source_path(rpath)
        # print("compile path " + compile_path)
        lib_workspace = self.compile_workspace(compile_path, rpath)

        if os.path.exists(lib_workspace):
            # print("current lib already link")
            return

        dir_path = os.path.dirname(os.path.realpath(__file__))
        print("begin link %s to %s" % (dir_path, lib_workspace))

        cdir = os.path.dirname(lib_workspace)
        print("cdir " + cdir)
        if not os.path.exists(cdir):
            os.makedirs(cdir)
        os.symlink(dir_path, lib_workspace)


if __name__ == '__main__':

    libs = [('libKWSing.a', ''), ("libKWLive.a", ''),
            ("libKWUtility_sub.a", ""),
            ('libcommon.a', '/common'),
            ('libOpenSource.a', '/OpenSource')]

    for lib in libs:
        fix = YTLibFix(lib)
        fix.main()
