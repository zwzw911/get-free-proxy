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
import helper.Helper as helper

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


def extra_data_from_page_xicidaili(soup):
    '''
    :param soup: 读取页面的html内容
    :return: list，当前页面所有proxy记录
    '''
    records = soup.select('#ip_list tr:not(:first-child)')
    result = []
    for single_record in records:
        ip = single_record.select('td:nth-of-type(2)')[0].string
        port = single_record.select('td:nth-of-type(3)')[0].string
        is_anonymous = single_record.select('td:nth-of-type(5)')[
            0].string
        is_anonymous = 'TRANS' if is_anonymous == '透明' else 'HIGH_ANON'
        protocol = single_record.select('td:nth-of-type(6)')[
            0].string.upper()
        # 期望是所有，直接添加
        if self_enum.ProxyType.All in setting.proxy_filter.type:
            result.append({'ip': ip, 'port': port, 'protocol': protocol,
                           'type': is_anonymous})
            # continue
        # 如果期望获得透明，且获得的proxy是透明，添加
        elif self_enum.ProxyType.Transparent in setting.proxy_filter.type:
            if is_anonymous == 'TRANS':
                result.append({'ip': ip, 'port': port, 'protocol': protocol,
                               'type': is_anonymous})
                # continue
        # 如果期望获得高匿，且获得的是高匿，添加
        elif self_enum.ProxyType.Anonymous in setting.proxy_filter.type or \
                self_enum.ProxyType.High16yun in setting.proxy_filter.type:
            if is_anonymous == 'HIGH_ANON':
                result.append({'ip': ip, 'port': port, 'protocol': protocol,
                               'type': is_anonymous})
                # continue
        # proxies.append({
        #     'http': '%s:%s' % (ip, port),
        #     'https': '%s:%s' % (ip, port)
        # })

    return result


def extra_data_from_page_kuaidaili(soup):
    '''
    :param soup: 读取页面的html内容
    :return: list，当前页面所有proxy记录
    '''
    records = soup.select('tbody>tr')
    result = []
    for single_record in records:
        ip = single_record.select('td[data-title=IP]')[0].string
        port = single_record.select('td[data-title=PORT]')[0].string
        is_anonymous = single_record.select('td[data-title=匿名度]')[
            0].string
        is_anonymous = 'TRANS' if is_anonymous == '透明' else 'HIGH_ANON'
        protocol = single_record.select('td[data-title=类型]')[
            0].string.upper()
        result.append({'ip': ip, 'port': port, 'protocol': protocol,
                       'type': is_anonymous})
    return result


def extra_data_from_page_proxylist(soup):
    '''
    :param soup: 读取页面的html内容
    :return: list，当前页面所有proxy记录
    '''
    # print(soup.string)
    records = soup.select('div.table>ul')
    result = []
    for single_record in records:
        raw_country = single_record.select('li.country-city>div>span.country')[
            0]
        print(raw_country)
        print(raw_country['title'])
        if self_enum.Country.All in setting.proxy_filter.country:
            pass
        elif
        raw_ip = single_record.select('li.proxy')[0].get_text()
        ip_base64 = re.match(r'Proxy\(\'(.*)\'\)', raw_ip).group(1)
        ip_str = base64.b64decode(ip_base64).decode('utf-8').split(':')
        ip = ip_str[0]
        port = ip_str[1]

        # for string in ip:
        #     print(string)
    #     port = single_record.select('td:nth-of-type(3)')[0].string
    #     is_anonymous = single_record.select('td:nth-of-type(5)')[
    #         0].string
    #     is_anonymous = 'TRANS' if is_anonymous == '透明' else 'HIGH_ANON'
    #     protocol = single_record.select('td:nth-of-type(6)')[
    #         0].string.upper()
    #     # 如果期望获得透明，但实际得到是高匿，则代理丢弃
    #     if setting.proxy_filter.type == self_enum.ProxyType.Transparent:
    #         if is_anonymous == 'HIGH_ANON':
    #             continue
    #     # 如果期望获得高匿，但实际得到是透明，则代理丢弃
    #     if setting.proxy_filter.type == self_enum.ProxyType.Anonymous or \
    #             setting.proxy_filter.type == self_enum.ProxyType.High16yun:
    #         if is_anonymous == 'TRANS':
    #             continue
    #     # proxies.append({
    #     #     'http': '%s:%s' % (ip, port),
    #     #     'https': '%s:%s' % (ip, port)
    #     # })
    #     result.append({'ip': ip, 'port': port, 'protocol': protocol,
    #                    'type': is_anonymous})
    # return result


def gen_proxy(site):
    '''
    :param site: list， 提供免费代理的url
    :return:
    '''
    headers = gen_header.gen_limit_header(50)

    result = []
    for single_site in site:
        if_use_proxy = helper.detect_if_need_proxy(single_site['urls'][0])
        if_proxy_usable = helper.detect_if_proxy_usable(
            proxies=setting.BASIC_PROXY, url=single_site['urls'][0])
        if not if_proxy_usable:
            logging.warning('代理%s无法连接到%s，忽略' % (setting.BASIC_PROXY,
                                                single_site['urls'][0]))
            continue

        if 'xicidaili' in single_site['urls'][0]:
            for single_url in single_site['urls']:
                header = random.choice(headers)
                soup = helper.send_request_get_response(url=single_url,
                                                        if_use_proxy=if_use_proxy,
                                                        proxies=setting.BASIC_PROXY,
                                                        header=header)
                result += extra_data_from_page_xicidaili(soup)
        if 'kuaidaili' in single_site['urls'][0]:
            for single_url in single_site['urls']:
                #  期望透明，但是url是指向高匿，则忽略
                if self_enum.ProxyType.Transparent in setting.proxy_filter.type:
                    if 'intr' not in single_url:
                        continue
                # 期望高匿，但是url指向透明，忽略
                if self_enum.ProxyType.Anonymous in setting.proxy_filter.type\
                        or self_enum.ProxyType.High16yun in \
                        setting.proxy_filter.type:
                    if 'inha' not in single_url:
                        continue
                header = random.choice(headers)
                soup = helper.send_request_get_response(url=single_url,
                                                        if_use_proxy=if_use_proxy,
                                                        proxies=setting.BASIC_PROXY,
                                                        header=header)
                result += extra_data_from_page_kuaidaili(soup)
        if 'proxy-list' in single_site['urls'][0]:
            for single_url in single_site['urls']:
                header = random.choice(headers)
                soup = helper.send_request_get_response(url=single_url,
                                                        if_use_proxy=if_use_proxy,
                                                        proxies=setting.BASIC_PROXY,
                                                        header=header)
                result += extra_data_from_page_proxylist(soup)
    return result


def check_proxies_validate(single_result, final_result):
    '''
    :param single_result:dict。 gen_proxy获得的结果中，单个记录。{ip,port,type,protocol}
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
    if helper.detect_if_proxy_usable(proxies=proxy):
        print('代理 %s 有效' % proxy['http'])
        final_result.append(single_result)
        return True
    else:
        print('代理 %s 无效' % proxy['http'])
        # final_result.append(single_result)
        return False


# def pool_run(proxies):
#     # task_list = []
#     # logging.debug(psutil.cpu_count())
#     print(time.time())
#     p = Pool(psutil.cpu_count())
#     # for single_proxy in proxies:
#     #     p.apply_async(check_proxies_validate, args=(single_proxy,))
#     p.apply_async(check_proxies_validate, args=(proxies[0],))
#     p.apply_async(check_proxies_validate, args=(proxies[1],))
#     print('Waiting for all subprocesses done...')
#     start_time = time.time()
#     p.close()
#     p.join()
#     end_time = time.time()
#     print('All subprocesses done. total cost %s ms' % (end_time-start_time))
#     # gevent.joinall(task_list)


def gevent_run(result):
    '''
    :param result: list。 页面中获得的代理，需要进行检测，是否valid
    :return: list(final_result)
    '''
    task_list = []
    # logging.debug(psutil.cpu_count())
    # print(proxies)
    # p = Pool(2)
    final_result = []
    for single_result in result:
        task_list.append(
            gevent.spawn(check_proxies_validate, single_result, final_result)
        )
        # p.apply_async(check_proxies_validate, args=(single_proxy,))
    # p.apply_async(check_proxies_validate, args=(proxies[1],))
    print('Waiting for gevent done...')
    start_time = time.time()
    gevent.joinall(task_list)
    end_time = time.time()
    print('All gevent done. total cost %s ms' % (end_time - start_time))
    print(final_result)


if __name__ == '__main__':
    # tmp_proxies = [{'http': '49.83.243.248:8118', 'https': '49.83.243.248:8118'},
    #            {'http': '42.55.252.102:1133', 'https': '42.55.252.102:1133'}]
    # wn: https代理        wt: http代理    透明/高匿混合在同一页面
    site = [
        # {
        #     'urls': ['https://www.xicidaili.com/%s/%s' % (m, n) for m in [
        #         'wn', 'wt'] for n in range(1, 3)],
        # },
        # {
        #     # inha：国内高匿   intr：国内透明
        #     'urls': ['https://www.kuaidaili.com/free/%s/%s' % (m, n) for m in
        #              ['inha', 'intr'] for n in range(1, 5)]
        # },
        {
            'urls': ['https://proxy-list.org/english/index.php?p=%s' for m
                     in range(1, 2)]
        },
    ]
    result = gen_proxy(site)
    print(result)
    # pool_run(tmp_proxies)
    # gevent_run(result)
