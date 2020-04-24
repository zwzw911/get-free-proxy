#! /usr/bin/env python3
# -*- coding:utf-8 -*-
'''
在发送request之前，预先进行过滤
'''

# from src import self as gfp_self_enum, setting
import get_free_proxy.self.SelfEnum as gfp_self_enum
# import get_free_proxy.setting.setting as setting

def pre_filter_xicidaili(setting):
    '''
    xici只支持HTTP/HTTPS， 如果setting.protocol中配置了HTTP/HTTPS，就返回True
    :param setting: gfp_setting
    :return: boolean。如果是True，说明通过，可以继续发送request；否则，无需发送request
    '''

    # xici不支持socks(只支持HTTP/HTTPS)，如果setting中只包含socks4/5，则不作任何处理
    # if gfp_self_enum.ProtocolType.ALL not in setting.proxy_filter['protocol']:
        # 没有ALL，但是有HTTP，返回True
    if gfp_self_enum.ProtocolType.HTTP in setting.protocol:
        return True
    # 没有ALL，但是有HTTPS，返回True
    if gfp_self_enum.ProtocolType.HTTPS in setting.protocol:
        return True
    return False
    # else:
    #     return True


def pre_filter_kuaidaili(setting):
    '''

    :param setting: gfp_setting
    '''

    # kuaidaili只支持HTTP，无国家
    return gfp_self_enum.ProtocolType.HTTP in setting.protocol
    # if gfp_self_enum.ProtocolType.ALL not in \
    #         setting.proxy_filter['protocol'] and \
    #         gfp_self_enum.ProtocolType.HTTP not in \
    #         setting.proxy_filter['protocol']:
    #     return False
    # return True


def pre_filter_proxy_list(setting):
    '''
    proxy-list只支持HTTP/HTTPS，和xicidaili一样，所以直接调用xicidaili
    :param setting: gfp_setting
    '''
    return pre_filter_xicidaili(setting)
# print(pre_filter_xicidaili())


def pre_filter_hidemy(setting):
    '''
    hidemy无需prefilter进行check
    :param setting: gfp_setting
    '''
    return True
