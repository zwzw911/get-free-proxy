#! /usr/bin/env python3
# -*- coding:utf-8 -*-

# import gevent
from requests_html import AsyncHTMLSession

asession = AsyncHTMLSession()
# import get_free_proxy.main.
import random
import logging

logging.basicConfig(level=logging.DEBUG)

# import gen-browser-header
# import src.generator.GenHeader as gen_header
import get_free_proxy.generator.GenProxyFromPage as gen_proxy_from_page
# import src.helper.Helper as helper
# import get_free_proxy.helper.PreFilter as pre_filter
import get_free_proxy.self.SelfEnum as gfp_self_enum
import get_free_proxy.setting.Setting as gfp_setting

import gen_browser_header.main.GenHeader as gen_header
import gen_browser_header.setting.Setting as gbh_setting
import gen_browser_header.helper.Helper as gbh_helper

import get_free_proxy.self.EnumMatchInst as gfp_enum_match_inst


def gen_proxy_sync(enum_site, sites, gfp_setting, headers, proxies):
    '''
    采用异步方式发送request，以提高效率
    首先获取sites中总共的url数量
    :params enum_site: enum，对那个网站获得代理信息
    :param sites: dict， setting.site的复制品
                    key为urls和need_proxy。{urls:[], need_proxy:boolean}
    :param gfp_setting:
    :param headers: list, 连接sites中所有url时，使用的header，为了保险，每个url使用不同的header
    :param proxies: list，如果site需要代理连接，使用的代理池，为了提高速度，数量和sites中的url数量一致
                    前提是，所有代理已经经过验证，可以连接到代理url
    :return:
    '''
    # headers = gen_header(50)
    result = []
    pre_filter_function = gfp_enum_match_inst.getPrefilterFunction(enum_site)
    if pre_filter_function is None:
        raise ValueError('无法根据网站名称%s找到对应的pre_filter函数' % enum_site.name)
    # xici不支持socks，如果setting中只包含socks4/5，则不作任何处理
    if not pre_filter_function():
        return

    if_use_proxy = sites['need_proxy']
    url_num = len(sites['urls'])
    for single_url in sites['urls']:
        # kuaidaili特殊处理
        if enum_site == gfp_self_enum.SupportedWeb.Kuai:
            #  期望透明，但是url是指向高匿，则忽略
            if gfp_self_enum.ProxyType.TRANS in \
                    gfp_setting.proxy_type:
                if 'intr' not in single_url:
                    continue
            # 期望高匿，但是url指向透明，忽略
            if gfp_self_enum.ProxyType.ANON in \
                    gfp_setting.proxy_type \
                    or gfp_self_enum.ProxyType.HIGH_ANON in \
                    gfp_setting.proxy_type:
                if 'inha' not in single_url:
                    continue
        header = headers.pop()
        proxy = None
        if if_use_proxy:
            if url_num <= len(proxies):
                proxy = proxies.pop()
            else:
                proxy = random.choice(proxies)

        soup = gbh_helper.send_request_get_response(
            url=single_url, if_use_proxy=if_use_proxy,
            proxies=proxy, header=header)
        extract_data_function = gfp_enum_match_inst.getExtractDataFunction(enum_site)
        if pre_filter_function is None:
            raise ValueError('无法根据网站名称%s找到对应的extract_data函数' % enum_site.name)
        result += extract_data_function(soup)
    return result


# def gen_proxy_sync(headers,setting):
#     '''
#     request采用同步方式，效率低，但是可靠
#     :param headers: 读取网页时，需要的headers
#     :param setting: gfp_setting
#     :return:
#     '''
#     headers = gen_header(50)
#     result = []
#     for single_site in site:
#         if_use_proxy = helper.detect_if_need_proxy(single_site['urls'][0])
#         if if_use_proxy:
#             if_proxy_usable = helper.detect_if_proxy_usable(
#                 proxies=setting.BASIC_PROXY, header=random.choice(
#                     headers), url=single_site['urls'][0])
#             if not if_proxy_usable:
#                 logging.warning('代理%s无法连接到%s，忽略' % (setting.BASIC_PROXY,
#                                                     single_site['urls'][0]))
#                 continue
#
#         if 'xicidaili' in single_site['urls'][0]:
#             # xici不支持socks，如果setting中只包含socks4/5，则不作任何处理
#             if not pre_filter.pre_filter_xicidaili():
#                 continue
#             for single_url in single_site['urls']:
#                 header = random.choice(headers)
#                 soup = helper.send_request_get_response(
#                     url=single_url, if_use_proxy=if_use_proxy,
#                     proxies=setting.BASIC_PROXY, header=header)
#                 result += \
#                     gen_proxy_from_page.extra_data_from_page_xicidaili(soup)
#
#         if 'kuaidaili' in single_site['urls'][0]:
#             # kuaidaili只支持HTTP，无国家
#             if not pre_filter.pre_filter_kuaidaili():
#                 continue
#             for single_url in single_site['urls']:
#                 #  期望透明，但是url是指向高匿，则忽略
#                 if self_enum.ProxyType.TRANS in \
#                         setting.proxy_filter['proxy_type']:
#                     if 'intr' not in single_url:
#                         continue
#                 # 期望高匿，但是url指向透明，忽略
#                 if self_enum.ProxyType.ANON in setting.proxy_filter[
#                     'type'] \
#                         or self_enum.ProxyType.HIGH_ANON in \
#                         setting.proxy_filter['proxy_type']:
#                     if 'inha' not in single_url:
#                         continue
#                 header = random.choice(headers)
#                 soup = helper.send_request_get_response(
#                     url=single_url, if_use_proxy=if_use_proxy,
#                     proxies=setting.BASIC_PROXY, header=header)
#                 result += gen_proxy_from_page.extra_data_from_page_kuaidaili(
#                     soup)
#
#         if 'proxy-list' in single_site['urls'][0]:
#             # proxy-list只支持HTTP/HTTPS
#             if not pre_filter.pre_filter_proxy_list():
#                 continue
#
#             for single_url in single_site['urls']:
#                 header = random.choice(headers)
#                 soup = helper.send_request_get_response(
#                     url=single_url, if_use_proxy=if_use_proxy,
#                     proxies=setting.BASIC_PROXY, header=header)
#                 result += gen_proxy_from_page.extra_data_from_page_proxylist(
#                     soup)
#
#         if 'hidemy' in single_site['urls'][0]:
#             # hidemy.name支持所有protocol，2种type，和国家
#             for single_url in single_site['urls']:
#                 header = random.choice(headers)
#                 soup = helper.send_request_get_response(
#                     url=single_url, if_use_proxy=if_use_proxy,
#                     proxies=setting.BASIC_PROXY, header=header)
#                 result += gen_proxy_from_page.extra_data_from_page_hidemy(
#                     soup)
#
#     return result

def gen_proxy_async(enum_site, sites, gfp_setting, headers, proxies, force_render=False):
    '''
    采用异步方式发送request，以提高效率
    首先获取sites中总共的url数量
    :param enum_site: enum，对那个网站获得代理信息
    :param sites: dict， setting.site的复制品
                    key为urls/enum_site和need_proxy。{urls:[], enum_site:Xici,need_proxy:boolean}
    :param gfp_setting:
    :param headers: list, 连接sites中所有url时，使用的header，为了保险，每个url使用不同的header
    :param proxies: list/None， None说明无需代理
                    如果site需要代理连接，使用的代理池。代理的数量可能小于sites.urls的数量。
                    如果代理的数量大于sites.urls，pop一个（使用的代理无重复）；否则，随机选择一个（可能重复）
                    前提是，所有代理已经经过验证，可以连接到代理url
    :param force_render: requests-html是否需要render页面（某些页面需要执行js才能显示html元素）
    :return:
    '''
    # # headers = gen_header.gen_limit_header(50)
    # print('gen_proxy_async start')
    # print('proxires %s' % proxies)
    result = []

    pre_filter_function = gfp_enum_match_inst.getPrefilterFunction(enum_site)
    if pre_filter_function is None:
        raise ValueError('无法根据网站名称%s找到对应的pre_filter函数' % enum_site.name)
    # xici不支持socks，如果setting中只包含socks4/5，则不作任何处理
    if not pre_filter_function(gfp_setting):
        # print('pre filter not pass')
        return
    # print('xici start')
    task_list = []

    if_use_proxy = sites['need_proxy']

    url_num = len(sites['urls'])
    if if_use_proxy:
        if_proxy_num_larger_than_url_num = url_num <= len(proxies)
    for single_url in sites['urls']:
        # kuaidaili特殊处理
        if enum_site == gfp_self_enum.SupportedWeb.Kuai:
            #  期望透明，但是url是指向高匿，则忽略
            if gfp_self_enum.ProxyType.TRANS in \
                    gfp_setting.proxy_type:
                if 'intr' not in single_url:
                    continue
            # 期望高匿，但是url指向透明，忽略
            if gfp_self_enum.ProxyType.ANON in \
                    gfp_setting.proxy_type \
                    or gfp_self_enum.ProxyType.HIGH_ANON in \
                    gfp_setting.proxy_type:
                if 'inha' not in single_url:
                    continue
        header = headers.pop()
        proxy = None
        if if_use_proxy:
            if if_proxy_num_larger_than_url_num:
                proxy = proxies.pop()
            else:
                proxy = random.choice(proxies)


        # print("if_use_proxy: %s" % if_use_proxy)
        # print('proxy is %s' % proxy)
        # print('header is %s' % header)
        # print('single_url is %s' % single_url)
        task_list.append(lambda url=single_url, if_use_proxy=if_use_proxy,
                                proxies=proxy, header=header,
                                force_render=force_render:
                                gbh_helper.async_send_request_get_response(
                                    url, if_use_proxy, proxies, header,
                                    force_render)
                         )

    raw_results = asession.run(*task_list)
    # print('raw result is %s' % raw_results)

    extract_data_function = gfp_enum_match_inst.getExtractDataFunction(enum_site)
    # logging.info('extract_data_function is %s' % extract_data_function)
    if extract_data_function is None:
        raise ValueError('无法根据网站名称%s找到对应的extract_data函数' % enum_site.name)
    # print(raw_results)

    for single_raw_result in raw_results:
        # print('single_raw_result.html is %s' % single_raw_result.html)
        # if force_render:
        #     await single_raw_result.html.arender()
            # print(single_raw_result)
        # logging.info('single_soup is %s' % single_soup)
        # print('single_raw_result.html after rendering %s' % single_raw_result.html)
        result += extract_data_function(single_raw_result, gfp_setting)
    # print('result is %s ' % result)
    return result


# def gen_proxy_async(sites, proxies):
#     '''
#     采用异步方式发送request，以提高效率
#     首先获取sites中总共的url数量
#     :param sites: list， 提供免费代理的url
#     :param proxies: list，如果site需要代理连接，使用的代理池
#     :return:
#     '''
#     headers = gen_header.gen_limit_header(50)
#     # print('gen_proxy_async start')
#     result = []
#     for single_site in site:
#         # print(single_site['urls'][0])
#         if_use_proxy = helper.detect_if_need_proxy(single_site['urls'][0])
#         # print('if_use_proxy %s' % if_use_proxy)
#         if if_use_proxy:
#             if_proxy_usable = helper.detect_if_proxy_usable(
#                 proxies=setting.BASIC_PROXY, header=random.choice(
#                     headers), url=single_site['urls'][0])
#             if not if_proxy_usable:
#                 logging.warning('代理%s无法连接到%s，忽略' % (setting.BASIC_PROXY,
#                                                     single_site['urls'][0]))
#                 continue
#
#         if 'xicidaili' in single_site['urls'][0]:
#             # xici不支持socks，如果setting中只包含socks4/5，则不作任何处理
#             if not pre_filter.pre_filter_xicidaili():
#                 continue
#             # print('xici start')
#             task_list = []
#             soup_list = []
#             for single_url in single_site['urls']:
#                 header = random.choice(headers)
#                 task_list.append(
#                     gevent.spawn(helper.async_send_request_get_response,
#                                  single_url, if_use_proxy,
#                                  setting.BASIC_PROXY, header, soup_list)
#                 )
#             gevent.joinall(task_list)
#             for single_soup in soup_list:
#                 result += \
#                     gen_proxy_from_page.extra_data_from_page_xicidaili(
#                         single_soup)
#         if 'kuaidaili' in single_site['urls'][0]:
#             # kuaidaili只支持HTTP，无国家
#             if not pre_filter.pre_filter_kuaidaili():
#                 continue
#
#             task_list = []
#             soup_list = []
#
#             for single_url in single_site['urls']:
#                 #  期望透明，但是url是指向高匿，则忽略
#                 if self_enum.ProxyType.TRANS in \
#                         setting.proxy_filter['proxy_type']:
#                     if 'intr' not in single_url:
#                         continue
#                 # 期望高匿，但是url指向透明，忽略
#                 if self_enum.ProxyType.ANON in \
#                         setting.proxy_filter['proxy_type'] \
#                         or self_enum.ProxyType.HIGH_ANON in \
#                         setting.proxy_filter['proxy_type']:
#                     if 'inha' not in single_url:
#                         continue
#                 header = random.choice(headers)
#                 task_list.append(
#                     gevent.spawn(helper.async_send_request_get_response,
#                                  single_url, if_use_proxy,
#                                  setting.BASIC_PROXY, header, soup_list)
#                 )
#             gevent.joinall(task_list)
#             for single_soup in soup_list:
#                 result += gen_proxy_from_page.extra_data_from_page_kuaidaili(
#                     single_soup)
#         if 'proxy-list' in single_site['urls'][0]:
#             # proxy-list只支持HTTP/HTTPS
#             if not pre_filter.pre_filter_proxy_list():
#                 continue
#
#             task_list = []
#             soup_list = []
#             for single_url in single_site['urls']:
#                 header = random.choice(headers)
#                 task_list.append(
#                     gevent.spawn(helper.async_send_request_get_response,
#                                  single_url, if_use_proxy,
#                                  setting.BASIC_PROXY, header, soup_list)
#                 )
#
#             gevent.joinall(task_list)
#             for single_soup in soup_list:
#                 result += gen_proxy_from_page.extra_data_from_page_proxylist(
#                     single_soup)
#             # print(result)
#         if 'hidemy' in single_site['urls'][0]:
#             task_list = []
#             soup_list = []
#             for single_url in single_site['urls']:
#                 header = random.choice(headers)
#                 task_list.append(
#                     gevent.spawn(helper.async_send_request_get_response,
#                                  single_url, if_use_proxy,
#                                  setting.BASIC_PROXY, header, soup_list)
#                 )
#
#             gevent.joinall(task_list)
#             for single_soup in soup_list:
#                 result += gen_proxy_from_page.extra_data_from_page_hidemy(
#                     single_soup)
#     return result


if __name__ == '__main__':
    # from requests_html import AsyncHTMLSession
    #
    # asession = AsyncHTMLSession()
    gen_proxy_async(enum_site=None,
                          sites=None,
                          gfp_setting=None,
                          headers=None,
                          proxies=None)
    # print(sys.path)
    # tmp_proxies = [{'http': '49.83.243.248:8118', 'https': '49.83.243.248:8118'},
    #            {'http': '42.55.252.102:1133', 'https': '42.55.252.102:1133'}]
    # checker.win_check_mysql_and_run()
    # import time
    # time.sleep(10)
    site = [
        {
            # wn: https代理        wt: http代理    透明/高匿混合在同一页面
            # socks代理验证时间太长，所以不采用
            'urls': ['https://www.xicidaili.com/%s/%s' % (m, n) for m in [
                'wn', 'wt'] for n in range(1, 2)],
        },
        # {
        #     # inha：国内高匿   intr：国内透明
        #     # kuaidaili只有http代理
        #     'urls': ['https://www.kuaidaili.com/free/%s/%s' % (m, n) for m in
        #              ['inha', 'intr'] for n in range(1, 2)]
        # },
        # {
        #     # proxy-list只有http/https代理
        #     'urls': ['https://proxy-list.org/english/index.php?p=%s' % m for m
        #              in range(1, 2)]
        # },
        # {
        #     # hidemy.name支持所有protocol，2种type，和国家
        #     'urls': ['https://hidemy.name/en/proxy-list/?start=%s#list' %
        #              str((m-1)*64) if m > 1 else
        #              'https://hidemy.name/en/proxy-list/?start=1#list'
        #              for m in range(1, 2)]
        # }
    ]
    # print(site)
    # result = gen_proxy_async(site=site)
    # print('__init__')
    # r = fast_validate_proxy(result)
    #
    # try:
    #     db_conn = db_mysql.MySql(host='127.0.0.1', user='root', pwd='1234')
    # except Exception as e:
    #     print(e)

    # db_conn.create_db()
    # db_conn.create_tbl()
    # try:
    #     # db_conn.insert(single_record=test_data.TEST_PROXY[0])
    #     db_conn.insert_multi(records=r)
    # except pymysql.err.IntegrityError as e:
    #     s = re.sub(r'[\(\)]','',str(e))
    #     err_code = s.split(',')[0]
    #     err_msg = s.split(',')[1]
    #     print(e)

    # db_conn.insert(single_record=test_data.TEST_PROXY[0])
    # pool_run(tmp_proxies)
