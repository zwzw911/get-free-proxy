#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import os, subprocess, time
import ctypes, sys


def check_os():
    if sys.platform == 'win32':
        return 'WIN'
    if sys.platform == 'linux2':
        return 'LINUX'



def win_is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def win_check_mysql_running(service='MySQL'):
    print('开始检查服务MySQL是否启动')
    task = subprocess.Popen('tasklist /nh | find /i "%s"' % service,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, shell=True)
    # print(task.stdout.readlines())
    if len(task.stdout.readlines()) == 0:
        print('服务MySQL尚未启动')
        return False
    else:
        print('服务MySQL已经启动')
        return True


def win_start_mysql(service='MySQL'):
    if 'WIN' == check_os():
        if win_is_admin():
            # 将要运行的代码加到这里
            # if not win_check_mysql_running():
            subprocess.Popen('net start %s' % service,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, shell=True)
        else:
            print('not admin')
            print(sys.version_info)
            if sys.version_info[0] == 3:
                ctypes.windll.shell32.ShellExecuteW(None, "runas",
                                                    sys.executable, __file__, None, 1)
                # time.sleep(10)

    if 'LINUX' == check_os():
        pass


if __name__ == '__main__':
    # win_check_mysql_and_run()
    pass