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
    All = 3


@unique
class ProtocolType(Enum):
    HTTP = 0
    HTTPS = 1
    SOCKS4 = 2
    SOCKS5 = 3
    SOCKS = 4
    ALL = 5

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

@unique
# sort -u a | awk '{print $1 " = " NR}'
class Country(Enum):
    Argentina = 1
    Australia = 2
    Bangladesh = 3
    Botswana = 4
    Brazil = 5
    Cambodia = 6
    Cameroon = 7
    China = 8
    Colombia = 9
    Czech = 10
    Denmark = 11
    Ecuador = 12
    Germany = 13
    Greece = 14
    Hong = 15
    Hungary = 16
    India = 17
    Indonesia = 18
    Iraq = 19
    Italy = 20
    Japan = 21
    Kazakhstan = 22
    Latvia = 23
    Malaysia = 24
    Mexico = 25
    Mongolia = 26
    Nepal = 27
    Pakistan = 28
    Peru = 29
    Philippines = 30
    Russia = 31
    Sweden = 32
    Syrian = 33
    Thailand = 34
    Turkey = 35
    Ukrain = 36
    United = 37
    All = 38

if __name__ == '__main__':
    import setting
    print(type(setting.proxy_filter['country']))
    # a=[Country.China]
    # print(Country['China'] in a)
    # print('All2' in Country.__members__)
    # print(Country.__members__.items())
    # for k,v in Country.__members__:
    #     print(k)
    #     print(v.value)