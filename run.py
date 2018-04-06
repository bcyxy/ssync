# -*- coding:utf-8 -*-

import conf
import os
import sys
os.chdir(sys.path[0])
sys.path.append("./src")
import signal
import time
from sync_ser import SyncSer


glb_run_mark = True
def quit_process(sig_num, frame):
    global glb_run_mark
    print("Program is going to stop.")
    glb_run_mark = False


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_process)
    sser = SyncSer()
    sser.start()

    while glb_run_mark:
        time.sleep(1)
