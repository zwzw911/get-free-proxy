#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import gevent
from gevent import monkey

monkey.patch_all()  # 用于将标准库中大部分阻塞式调用修改为协作式运行, 3.7需要最先import

import sys
import base64
import re

sys.path.append('..')
import generator.GenHeader as gen_header
import generator.GenProxyFromPage as gen_proxy_from_page
import helper.Helper as helper
import helper.PreFilter as pre_filter

import setting
import random
import psutil
from multiprocessing import Queue, Pool
import logging
import time

logging.basicConfig(level=logging.DEBUG)

import self.SelfEnum as self_enum

FREE_PROXY_SITE = [
    # {
    #     # firefox报告安全问题
    #     'urls': ['http://www.66ip.cn/%s.html' % n for n in
    #              ['index'] + list(range(2, 12))],
    #     'type': 'xpath',
    #     'pattern': ".//*[@id='main']/div/div[1]/table/tr[position()>1]",
    #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]',
    #                  'protocol': ''}
    # },
    # {
    #     'urls': ['http://www.66ip.cn/areaindex_%s/%s.html' % (m, n) for m in
    #              range(1, 35) for n in range(1, 10)],
    #     'type': 'xpath',
    #     'pattern': ".//*[@id='footer']/div/table/tr[position()>1]",
    #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]',
    #                  'protocol': ''}
    # },
    # {
    #     # 安全问题
    #     'urls': ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218'],
    #     'type': 'xpath',
    #     'pattern': ".//table[@class='sortable']/tbody/tr",
    #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
    #                  'protocol': ''}
    #
    # },
    # {
    #     # 安全问题
    #     'urls': ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 10)],
    #     'type': 'xpath',
    #     'pattern': ".//table[@class='list']/tr",
    #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
    #                  'protocol': ''}
    #
    # },

    {
        'urls': ['http://incloak.com/proxy-list/%s#list' % n for n in
                 ([''] + ['?start=%s' % (64 * m) for m in range(1, 10)])],
        'type': 'xpath',
        'pattern': ".//table[@class='proxy__t']/tbody/tr",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
                     'protocol': ''}

    },
    {
        'urls': ['http://www.kuaidaili.com/proxylist/%s/' % n for n in
                 range(1, 11)],
        'type': 'xpath',
        'pattern': ".//*[@id='index_free_list']/table/tbody/tr[position()>0]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]',
                     'protocol': './td[4]'}
    },
    # {
    #     'urls': ['http://www.kuaidaili.com/free/%s/%s/' % (m, n) for m in
    #              ['inha', 'intr', 'outha', 'outtr'] for n in
    #              range(1, 11)],
    #     'type': 'xpath',
    #     'pattern': ".//*[@id='list']/table/tbody/tr[position()>0]",
    #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]',
    #                  'protocol': './td[4]'}
    # },
    {
        'urls': ['http://www.cz88.net/proxy/%s' % m for m in
                 ['index.shtml'] + ['http_%s.shtml' % n for n in range(2, 11)]],
        'type': 'xpath',
        'pattern': ".//*[@id='boxright']/div/ul/li[position()>1]",
        'position': {'ip': './div[1]', 'port': './div[2]', 'type': './div[3]',
                     'protocol': ''}

    },
    {
        'urls': ['http://www.ip181.com/daili/%s.html' % n for n in
                 range(1, 11)],
        'type': 'xpath',
        'pattern': ".//div[@class='row']/div[3]/table/tbody/tr[position()>1]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]',
                     'protocol': './td[4]'}

    },
    # {
    #     'urls': ['http://www.xicidaili.com/%s/%s' % (m, n) for m in
    #              ['nn', 'nt', 'wn', 'wt'] for n in range(1, 8)],
    #     'type': 'xpath',
    #     'pattern': ".//*[@id='ip_list']/tr[position()>1]",
    #     'position': {'ip': './td[2]', 'port': './td[3]', 'type': './td[5]',
    #                  'protocol': './td[6]'}
    # },
    {
        'urls': ['http://www.cnproxy.com/proxy%s.html' % i for i in
                 range(1, 11)],
        'type': 'module',
        'moduleName': 'CnproxyPraser',
        'pattern': r'<tr><td>(\d+\.\d+\.\d+\.\d+)<SCRIPT type=text/javascript>document.write\(\"\:\"(.+)\)</SCRIPT></td><td>(HTTP|SOCKS4)\s*',
        'position': {'ip': 0, 'port': 1, 'type': -1, 'protocol': 2}
    }
]


# if len(site['urls']) == 0:
#     return None
# def get_page_data(url, header, if_use_proxy):
#     '''
#     :param url: 代理信息的url
#     :param header： 发送到此url的request中，header的设置
#     :param if_use_proxy： 连接到此rul，是否需要代理
#     :return: soup/None（连接不到url）
#     '''
#     return helper.send_request_get_response(url=url, if_use_proxy=if_use_proxy,
#                                             proxies=setting.BASIC_PROXY,
#                                             header=header)

def gen_proxy_sync(*, site):
    '''
    request采用同步方式，效率低，但是可靠
    :param site:
    :return:
    '''
    headers = gen_header.gen_limit_header(50)
    result = []
    for single_site in site:
        if_use_proxy = helper.detect_if_need_proxy(single_site['urls'][0])
        if if_use_proxy:
            if_proxy_usable = helper.detect_if_proxy_usable(
                proxies=setting.BASIC_PROXY, header=random.choice(
                    headers), url=single_site['urls'][0])
            if not if_proxy_usable:
                logging.warning('代理%s无法连接到%s，忽略' % (setting.BASIC_PROXY,
                                                    single_site['urls'][0]))
                continue

        if 'xicidaili' in single_site['urls'][0]:
            # xici不支持socks，如果setting中只包含socks4/5，则不作任何处理
            if not pre_filter.pre_filter_xicidaili():
                continue
            for single_url in single_site['urls']:
                header = random.choice(headers)
                soup = helper.send_request_get_response(
                    url=single_url, if_use_proxy=if_use_proxy,
                    proxies=setting.BASIC_PROXY, header=header)
                result += \
                    gen_proxy_from_page.extra_data_from_page_xicidaili(soup)

        if 'kuaidaili' in single_site['urls'][0]:
            # kuaidaili只支持HTTP，无国家
            if not pre_filter.pre_filter_kuaidaili():
                continue
            for single_url in single_site['urls']:
                #  期望透明，但是url是指向高匿，则忽略
                if self_enum.ProxyType.Transparent in \
                        setting.proxy_filter['type']:
                    if 'intr' not in single_url:
                        continue
                # 期望高匿，但是url指向透明，忽略
                if self_enum.ProxyType.Anonymous in setting.proxy_filter[
                    'type'] \
                        or self_enum.ProxyType.High16yun in \
                        setting.proxy_filter['type']:
                    if 'inha' not in single_url:
                        continue
                header = random.choice(headers)
                soup = helper.send_request_get_response(
                    url=single_url, if_use_proxy=if_use_proxy,
                    proxies=setting.BASIC_PROXY, header=header)
                result += gen_proxy_from_page.extra_data_from_page_kuaidaili(
                    soup)

        if 'proxy-list' in single_site['urls'][0]:
            # proxy-list只支持HTTP/HTTPS
            if not pre_filter.pre_filter_proxy_list():
                continue

            for single_url in single_site['urls']:
                header = random.choice(headers)
                soup = helper.send_request_get_response(
                    url=single_url, if_use_proxy=if_use_proxy,
                    proxies=setting.BASIC_PROXY, header=header)
                result += gen_proxy_from_page.extra_data_from_page_proxylist(
                    soup)

        if 'hidemy' in single_site['urls'][0]:
            # hidemy.name支持所有protocol，2种type，和国家
            for single_url in single_site['urls']:
                header = random.choice(headers)
                soup = helper.send_request_get_response(
                    url=single_url, if_use_proxy=if_use_proxy,
                    proxies=setting.BASIC_PROXY, header=header)
                result += gen_proxy_from_page.extra_data_from_page_hidemy(
                    soup)

    return result

def gen_proxy_async(*, site):
    '''
    采用异步方式发送request，以提高效率
    :param site: list， 提供免费代理的url
    :return:
    '''
    headers = gen_header.gen_limit_header(50)
    # print('gen_proxy_async start')
    result = []
    for single_site in site:
        # print(single_site['urls'][0])
        if_use_proxy = helper.detect_if_need_proxy(single_site['urls'][0])
        # print('if_use_proxy %s' % if_use_proxy)
        if if_use_proxy:
            if_proxy_usable = helper.detect_if_proxy_usable(
                proxies=setting.BASIC_PROXY, header=random.choice(
                    headers), url=single_site['urls'][0])
            if not if_proxy_usable:
                logging.warning('代理%s无法连接到%s，忽略' % (setting.BASIC_PROXY,
                                                    single_site['urls'][0]))
                continue

        if 'xicidaili' in single_site['urls'][0]:
            # xici不支持socks，如果setting中只包含socks4/5，则不作任何处理
            if not pre_filter.pre_filter_xicidaili():
                continue
            print('xici start')
            task_list = []
            soup_list = []
            for single_url in single_site['urls']:
                header = random.choice(headers)
                task_list.append(
                    gevent.spawn(helper.async_send_request_get_response,
                                 single_url, if_use_proxy,
                                 setting.BASIC_PROXY, header, soup_list)
                )
            gevent.joinall(task_list)
            for single_soup in soup_list:
                result += \
                    gen_proxy_from_page.extra_data_from_page_xicidaili(
                        single_soup)
        if 'kuaidaili' in single_site['urls'][0]:
            # kuaidaili只支持HTTP，无国家
            if not pre_filter.pre_filter_kuaidaili():
                continue

            task_list = []
            soup_list = []

            for single_url in single_site['urls']:
                #  期望透明，但是url是指向高匿，则忽略
                if self_enum.ProxyType.Transparent in \
                        setting.proxy_filter['type']:
                    if 'intr' not in single_url:
                        continue
                # 期望高匿，但是url指向透明，忽略
                if self_enum.ProxyType.Anonymous in \
                        setting.proxy_filter['type'] \
                        or self_enum.ProxyType.High16yun in \
                        setting.proxy_filter['type']:
                    if 'inha' not in single_url:
                        continue
                header = random.choice(headers)
                task_list.append(
                    gevent.spawn(helper.async_send_request_get_response,
                                 single_url, if_use_proxy,
                                 setting.BASIC_PROXY, header, soup_list)
                )
            gevent.joinall(task_list)
            for single_soup in soup_list:
                result += gen_proxy_from_page.extra_data_from_page_kuaidaili(
                    single_soup)
        if 'proxy-list' in single_site['urls'][0]:
            # proxy-list只支持HTTP/HTTPS
            if not pre_filter.pre_filter_proxy_list():
                continue

            task_list = []
            soup_list = []
            for single_url in single_site['urls']:
                header = random.choice(headers)
                task_list.append(
                    gevent.spawn(helper.async_send_request_get_response,
                                 single_url, if_use_proxy,
                                 setting.BASIC_PROXY, header, soup_list)
                )

            gevent.joinall(task_list)
            for single_soup in soup_list:
                result += gen_proxy_from_page.extra_data_from_page_proxylist(
                    single_soup)
            # print(result)
        if 'hidemy' in single_site['urls'][0]:
            task_list = []
            soup_list = []
            for single_url in single_site['urls']:
                header = random.choice(headers)
                task_list.append(
                    gevent.spawn(helper.async_send_request_get_response,
                                 single_url, if_use_proxy,
                                 setting.BASIC_PROXY, header, soup_list)
                )

            gevent.joinall(task_list)
            for single_soup in soup_list:
                result += gen_proxy_from_page.extra_data_from_page_hidemy(
                    single_soup)
    return result


def check_proxies_validate(single_result, header, final_result):
    '''
    :param single_result:dict。 gen_proxy获得的结果中，单个记录。{ip,port,type,protocol}
    :param header: request的header
    :param final_result:list。为了在协程中直接将valid的proxy提取，直接传入此参数
    :return: boolean。实际上，使用协程时，无法使用此返回值，而是直接将结果放入final_result
    '''
    ip = single_result['ip']
    port = single_result['port']
    proxy = {
        'http': '%s:%s' % (ip, port),
        'https': '%s:%s' % (ip, port)
    }
    print('check_proxies start')
    # print(proxy)
    if helper.detect_if_proxy_usable(proxies=proxy, header=header):
        print('代理 %s 有效' % proxy['http'])
        final_result.append(single_result)
        return True
    else:
        print('代理 %s 无效' % proxy['http'])
        # final_result.append(single_result)
        return False


def fast_validate_proxy(result):
    '''
    :param result: list。 页面中获得的代理，需要进行检测，是否valid
    :return: list(final_result)
    '''
    task_list = []
    # logging.debug(psutil.cpu_count())
    # print(proxies)
    # p = Pool(2)
    final_result = []
    if len(result) > 10:
        headers = gen_header.gen_limit_header(len(result))
    else:
        headers = gen_header.gen_limit_header(1)

    for single_result in result:
        header = random.choice(headers)
        task_list.append(
            gevent.spawn(check_proxies_validate, single_result,
                         header, final_result)
        )
        # p.apply_async(check_proxies_validate, args=(single_proxy,))
    # p.apply_async(check_proxies_validate, args=(proxies[1],))
    print('Waiting for gevent done...')
    start_time = time.time()
    gevent.joinall(task_list)
    end_time = time.time()
    print('All gevent done. total cost %s ms' % (end_time - start_time))
    print(final_result)
    return final_result

if __name__ == '__main__':
    # tmp_proxies = [{'http': '49.83.243.248:8118', 'https': '49.83.243.248:8118'},
    #            {'http': '42.55.252.102:1133', 'https': '42.55.252.102:1133'}]

    site = [
        # {
        #     # wn: https代理        wt: http代理    透明/高匿混合在同一页面
        #     # socks代理验证时间太长，所以不采用
        #     'urls': ['https://www.xicidaili.com/%s/%s' % (m, n) for m in [
        #         'wn', 'wt'] for n in range(1, 4)],
        # },
        # {
        #     # inha：国内高匿   intr：国内透明
        #     # kuaidaili只有http代理
        #     'urls': ['https://www.kuaidaili.com/free/%s/%s' % (m, n) for m in
        #              ['inha', 'intr'] for n in range(1, 5)]
        # },
        # {
        #     # proxy-list只有http/https代理
        #     'urls': ['https://proxy-list.org/english/index.php?p=%s' % m for m
        #              in range(1, 2)]
        # },
        {
            # hidemy.name支持所有protocol，2种type，和国家
            'urls': ['https://hidemy.name/en/proxy-list/?start=%s#list' %
                     str((m-1)*64) if m > 1 else
                     'https://hidemy.name/en/proxy-list/?start=1#list'
                     for m in range(1, 3)]
        }
    ]
    print(site)
    result = gen_proxy_async(site=site)
    print(result)
    # pool_run(tmp_proxies)
    r = fast_validate_proxy(result)
    print(r)
