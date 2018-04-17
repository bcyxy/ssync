# -*- coding:utf-8 -*-

import conf
import fs_opt
import logging
import os
import re
import ssh_opt
import threading
import time


class SyncSer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        
        # 路径信息表
        # 功能：用于记录指定目录下，所有的目录的信息；
        # 结构: {路径: [路径类型, 文件修改时间, 路径状态]}
        #     路径类型取值：
        #         "f": 文件
        #         "d": 文件夹
        #     文件状态取值：
        #         "keep": 文件未变化
        #         "del": 已删除的文件
        #         "chg": 发生变化的文件
        self.file_info_table = {}
        self.sshOpt = ssh_opt.SshOpt()
        self.ign_path_reg = re.compile(conf.ignore_paths_exp)

    def run(self):
        self.__update_fpaths("keep")
        while True:
            time.sleep(0.5)
            is_ok = self.__update_fpaths("chg")
            if not is_ok:
                continue
            chg_count = self.__chk_file_chg()
            if chg_count == 0:
                continue
            self.__upload_chg_files()

    # 更新本地文件目录
    def __update_fpaths(self, new_path_status):
        path_list = fs_opt.get_paths(conf.local_dir)
        if len(path_list) == 0:
            logging.warning("Local path '' not exists.")
            return False

        for (abs_path, path_type) in path_list:
            rel_path = os.path.relpath(abs_path, conf.local_dir).replace("\\", "/")
            if rel_path == ".":
                continue
            re_rst = self.ign_path_reg.findall(rel_path)
            if len(re_rst) > 0:
                continue
            if self.file_info_table.get(rel_path, None) == None:
                self.file_info_table[rel_path] = [path_type, 0, new_path_status]
        return True

    #--检查文件变化
    def __chk_file_chg(self):
        chg_counter = 0
        for (rel_path, infos) in self.file_info_table.items():
            abs_path = os.path.join(conf.local_dir, rel_path).replace("\\", "/")
            if os.path.exists(abs_path):
                file_curr_tm = os.path.getmtime(abs_path)
                if file_curr_tm !=  infos[1]:
                    if infos[0] == "f" and infos[1] != 0:
                        infos[2] = "chg"
                    infos[1] = file_curr_tm
            else:
                infos[2] = "del"
            if infos[2] != "keep":
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
        for (rel_path, infos) in self.file_info_table.items():
            if infos[2] == "keep":
                continue
            
            local_path = os.path.join(conf.local_dir, rel_path).replace("\\", "/")
            remote_path = os.path.join(conf.remote_dir, rel_path).replace("\\", "/")
            if infos[2] == "chg":
                if infos[0] == "f":
                    r_fdir = os.path.dirname(remote_path).replace("\\", "/")
                    logging.info("Upload file '%s' begin ..." %rel_path)
                    if self.sshOpt.put(local_path, r_fdir):
                        logging.info("Upload file '%s' success." %rel_path)
                        infos[2] = "keep"
                elif infos[0] == "d":
                    if self.sshOpt.mkdir(remote_path):
                        logging.info("Remote mkdir '%s' success." %rel_path)
                        infos[2] = "keep"
            elif infos[2] == "del":
                logging.info("Remove remote file '%s' begin ..." %rel_path)
                if self.sshOpt.rm(remote_path):
                    del_paths.append(rel_path)
                    logging.info("Remove remote file '%s' success." %rel_path)
                    infos[2] = "keep"                

        for del_path in del_paths:
            self.file_info_table.pop(del_path)

        self.sshOpt.close()
