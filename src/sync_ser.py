# -*- coding:utf-8 -*-

import conf
import fs_opt
import logging
import os
import ssh_opt
import threading
import time


class SyncSer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        
        # 文件信息表
        # 功能：用于记录指定目录下，所有的文件的信息；
        # 结构: {文件路径: [文件修改时间, 文件状态]}
        #     文件状态取值：
        #         "keep": 文件未变化
        #         "del": 已删除的文件
        #         "chg": 发生变化的文件
        self.file_info_table = {}
        self.sshOpt = ssh_opt.SshOpt()

    def run(self):
        self.__remote_compare()
        while True:
            time.sleep(0.5)
            is_ok = self.__update_fpaths()
            if not is_ok:
                continue
            chg_count = self.__chk_file_chg()
            if chg_count <= 0:
                continue
            self.__upload_chg_files()

    # 与远端目录对比
    def __remote_compare(self):
        #TODO
        pass

    # 更新本地文件目录
    def __update_fpaths(self):
        files = fs_opt.get_files(conf.local_dir)
        for fpath in files:
            if self.file_info_table.get(fpath, None) == None:
                self.file_info_table[fpath] = [0, "chg"]
        return True

    #--检查文件变化
    def __chk_file_chg(self):
        chg_counter = 0
        for (fpath, infos) in self.file_info_table.items():
            if os.path.exists(fpath):
                file_curr_tm = os.path.getmtime(fpath)
                if file_curr_tm !=  infos[0]:
                    infos[0] = file_curr_tm
                    infos[1] = "chg"
            else:
                infos[1] = "del"
            if infos[1] != "keep":
                chg_counter += 1
        return chg_counter

    #--上传变化的文件
    def __upload_chg_files(self):
        is_ok = self.sshOpt.conn(conf.remote_host, conf.remote_port,
                                 conf.remote_user, conf.remote_passwd)
        if not is_ok:
            logging.warning("Connect remote failed.")
            return False

        del_paths = []
        for (fpath, infos) in self.file_info_table.items():
            if infos[1] == "keep":
                continue

            sub_fpath = fpath.replace(conf.local_dir, "").replace("\\", "/").strip("/")
            remote_fpath = os.path.join(conf.remote_dir, sub_fpath).replace("\\", "/")
            remote_fdir = os.path.dirname(remote_fpath)
            
            is_ok = False
            if infos[1] == "chg":
                logging.info("Upload file '%s' begin ..." %fpath)
                if self.sshOpt.put(fpath, remote_fdir):
                    logging.info("Upload file '%s' success." %fpath)
                    is_ok = True
            elif infos[1] == "del":
                logging.info("Remove remote file '%s' begin ..." %remote_fpath)
                if self.sshOpt.rm(remote_fpath):
                    del_paths.append(fpath)
                    logging.info("Remove remote file '%s' success." %remote_fpath)
                    is_ok = True

            if is_ok:
                infos[1] = "keep"

        for del_path in del_paths:
            self.file_info_table.pop(del_path)

        self.sshOpt.close()
