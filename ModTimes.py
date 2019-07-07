#!/usr/bin/python

from os import stat, utime

def CompareMtimes(f1,f2):
    f1_mtime = stat(f1).st_mtime
    f2_mtime = stat(f2).st_mtime

    if (int(f1_mtime) == int(f2_mtime)):
        return True
    return False