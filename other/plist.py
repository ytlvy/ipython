#!/usr/bin/env python
# -*- coding: utf-8 -*-



if __name__ == '__main__':
    for x in xrange(1,30):
        print ("<dict>")
        print ("    <key>id</key>")
        print ("    <string>{0:d}</string>").format(x)
        print ("    <key>small_img</key>")
        print ("    <string>表情_{0:d}.png</string>").format(x)
        print ("    <key>img</key>")
        print ("    <string>表情_{0:d}.png</string>").format(x)
        print ("    <key>chartlet</key>")
        print ("    <string>表情_{0:d}</string>").format(x)
        print ("</dict>")