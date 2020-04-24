#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# 需要将某些实体（函数）通过枚举引用

__author__ = 'zwzw911'

from enum import Enum, unique


import get_free_proxy.helper.PreFilter as prefilter
import get_free_proxy.generator.GenProxyFromPage as gen_proxy_from_page
import get_free_proxy.self.SelfEnum as gfp_self_enum
import gen_browser_header.helper.Helper as gbh_helper

def getPrefilterFunction(webenum):
    '''
    根据enum SupportedWeb的名字，返回对应的prefilter函数，如果没有出错，返回None
    :param webenum:
    :return: function
    '''
    if not gbh_helper.match_expect_type(webenum, 'SupportedWeb'):
        return

    if webenum.name == gfp_self_enum.SupportedWeb.Xici.name:
        return prefilter.pre_filter_xicidaili
    if webenum.name == gfp_self_enum.SupportedWeb.Kuai.name:
        return prefilter.pre_filter_kuaidaili
    if webenum.name == gfp_self_enum.SupportedWeb.Proxylist.name:
        return prefilter.pre_filter_proxy_list
    if webenum.name == gfp_self_enum.SupportedWeb.Hidemy.name:
        return prefilter.pre_filter_hidemy

    return

def getExtractDataFunction(webenum):
    '''
    根据enum SupportedWeb的名字，返回对应的prefilter函数，如果没有出错，返回None
    :param webenum:
    :return: function
    '''
    if not gbh_helper.match_expect_type(webenum, 'SupportedWeb'):
        return

    if webenum.name == gfp_self_enum.SupportedWeb.Xici.name:
        return gen_proxy_from_page.extra_data_from_page_xicidaili
    if webenum.name == gfp_self_enum.SupportedWeb.Kuai.name:
        return gen_proxy_from_page.extra_data_from_page_kuaidaili
    if webenum.name == gfp_self_enum.SupportedWeb.Proxylist.name:
        return gen_proxy_from_page.extra_data_from_page_proxylist
    if webenum.name == gfp_self_enum.SupportedWeb.Hidemy.name:
        return gen_proxy_from_page.extra_data_from_page_hidemy

    return


if __name__ == '__main__':
    k = gfp_self_enum.SupportedWeb.Xici
    print(type(k))
    # print(PreFilterFunction[k])
    # print(getPrefilterFunction(gfp_self_enum.SupportedWeb.Xici))