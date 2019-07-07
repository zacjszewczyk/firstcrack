#!/usr/local/bin/python3

import hashlib

BUF_SIZE = 65536  # 64kb chunks

def HashFiles(f1, f2):
    f1_md5 = hashlib.md5()
    f2_md5 = hashlib.md5()

    with open(f1, 'rb') as f1_fd, open(f2, 'rb') as f2_fd:
        while True:
            f1_data = f1_fd.read(BUF_SIZE)
            f2_data = f2_fd.read(BUF_SIZE)
            if (not f1_data) or (not f2_data):
                break
            f1_md5.update(f1_data)
            f2_md5.update(f2_data)

    if (f1_md5.hexdigest() != f2_md5.hexdigest()):
        return False
    return True
