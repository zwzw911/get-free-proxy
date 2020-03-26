#! /usr/bin/env python3

# -*- coding:utf-8 -*-

__author__ = 'zwzw911'

from enum import Enum, unique


@unique
class ProxyType(Enum):
    # 透明：对方服务器知道你使用了代理，也知道你的真实IP。
    # REMOTE_ADDR = ProxyIP，HTTP_VIA = ProxyIP，HTTP_X_FORWARDED_FOR = YourIP
    Transparent = 0
    # 匿名：对方服务器知道你使用了代理，但不知道你的真实IP。
    # REMOTE_ADDR = ProxyIP，HTTP_VIA = ProxyIP，HTTP_X_FORWARDED_FOR = ProxyIP
    Anonymous = 1
    # 高匿名：对方服务器不知道你使用了代理，也不知道你的真实IP。
    # REMOTE_ADDR = ProxyIP，HTTP_VIA = NULL，HTTP_X_FORWARDED_FOR = NULL
    High16yun = 2


@unique
class ProtocolType(Enum):
    Http = 0
    Https = 1


@unique
class ChromeType(Enum):
    Stable = 0  #稳定版
    Beta = 1    #测试版
    Dev = 2      #开发版
    Canary = 3  #金丝雀版
    All = 4     #所有版本

@unique
class OsType(Enum):
    Win32 = 0
    Win64 = 1
    All = 2
