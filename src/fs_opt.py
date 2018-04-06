# -*- coding:utf-8 -*-

import os
import sys

# 递归获取目录下的所有的文件
def get_files(dir_name):
    file_list = []
    if os.path.isfile(dir_name):
        file_list.append(dir_name)
        return file_list

    for f_d in os.listdir(dir_name):
        new_dir=os.path.join(dir_name,f_d)
        file_list += get_files(new_dir)

    return file_list
