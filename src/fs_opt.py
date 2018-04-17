# -*- coding:utf-8 -*-

import os
import sys

# 递归获取目录下的所有的文件
def get_paths(path):
    path_list = []
    if os.path.isfile(path):
        path_list.append((path, "f"))
        return path_list
    path_list.append((path, "d"))

    for sub_path in os.listdir(path):
        new_path = os.path.join(path, sub_path).replace("\\", "/")
        path_list += get_paths(new_path)

    return path_list
