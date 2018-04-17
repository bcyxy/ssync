# -*- coding:utf-8 -*-

local_dir = "D:/my_room/rsync_test"
remote_host = "192.168.11.249"
remote_port = 22
remote_dir = "/home/yxy/ssync_test"
remote_user = "yxy"
remote_passwd = "666666"
ignore_paths_exp = r'(ignore_path)'

import logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s|%(levelname)s|%(message)s',
    datefmt = '%Y%m%d_%H%M%S'
)

# 设置paramiko模块的日志级别
logging.getLogger("paramiko").setLevel(logging.WARNING)
