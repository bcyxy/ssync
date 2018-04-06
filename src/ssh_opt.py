# -*- coding:utf-8 -*-

import logging
import os
import paramiko
import time


class SshOpt(object):
    def __init__(self):
        self.tr_hd = None
        self.sftp_hd = None
        self.ssh_hd = None

    def conn(self, host, port, user, passwd):
        try:
            self.tr_hd = paramiko.Transport((host, port))
        except:
            return False

        self.tr_hd.connect(username = user, password = passwd)
        self.ssh_hd = paramiko.SSHClient()
        self.ssh_hd._transport = self.tr_hd
        self.sftp_hd = paramiko.SFTPClient.from_transport(self.tr_hd)

        return True

    def close(self):
        self.tr_hd.close()

    def put(self, local_fpath, remote_fdir):
        fname = os.path.basename(local_fpath)
        if not self.mkdir(remote_fdir):
            return False
        time.sleep(0.1)  # paramiko远程执行命令，一段时间后才能成功
        try:
            self.sftp_hd.put(local_fpath, remote_fdir+"/"+fname)
        except:
            return False
        return True

    def mkdir(self, dir):
        cmd = "mkdir -p %s" %dir
        stdin, stdout, stderr = self.ssh_hd.exec_command(cmd)
        if len(stderr.read()) > 0:
            return False
        return True

    def rm(self, path):
        cmd = "rm -rf %s" %path
        stdin, stdout, stderr = self.ssh_hd.exec_command(cmd)
        if len(stderr.read()) > 0:
            return False
        return True
