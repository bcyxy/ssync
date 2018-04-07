# ssync
Automatic, fast upload local changed files in specified folder to remote host.

## 需求
- 有许多Linux上运行的项目，开发时没有一个好的IDE。大部分的IDE在windows下运行，如何在windows下编码，在Linux下编译运行？本项目为解决这一问题建立。
- 现在的linux发行版本一般都自带ssh服务和sftp服务，本项目使用此两种服务，实现信息传输；
- 本地主机可以是windows、Linux系统，远端的主机必须是Linux系统；

## 功能
- 对比本地和远端的文件，如果有差异，将本地的文件更新到远端；
- 本地文件有变化，自动更新到远程服务器；

## 依赖
- python3
- paramiko

## 使用
- 配置：
  - conf.py文件
    - 配置本地路径、远端路径、远端主机连接的信息；
- 运行：
  - Linux环境：`python3 run.py`
  - Windows环境：双击`run.py`文件
