#! /usr/bin/env python3
# -*- coding:utf-8 -*-
'''
在发送request之前，预先进行过滤
'''

import setting
import self.SelfEnum as self_enum


def pre_filter_xicidaili():
    '''
    :return: boolean。如果是True，说明通过，可以继续发送request；否则，无需发送request
    '''

    # xici不支持socks(只支持HTTP/HTTPS)，如果setting中只包含socks4/5，则不作任何处理
    if self_enum.ProtocolType.ALL not in setting.proxy_filter['protocol']:
        # 没有ALL，但是有HTTP，返回True
        if self_enum.ProtocolType.HTTP in setting.proxy_filter['protocol']:
            return True
        # 没有ALL，但是有HTTPS，返回True
        if self_enum.ProtocolType.HTTPS in setting.proxy_filter['protocol']:
            return True
        return False
    else:
        return True


def pre_filter_kuaidaili():
    # kuaidaili只支持HTTP，无国家
    if self_enum.ProtocolType.ALL not in \
            setting.proxy_filter['protocol'] and \
            self_enum.ProtocolType.HTTP not in \
            setting.proxy_filter['protocol']:
        return False
    return True


def pre_filter_proxy_list():
    # proxy-list只支持HTTP/HTTPS，和xicidaili一样，所以直接调用xicidaili
    return pre_filter_xicidaili()
# print(pre_filter_xicidaili())
