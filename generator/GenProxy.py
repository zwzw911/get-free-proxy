#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import gevent
from gevent import monkey
monkey.patch_all()      # 用于将标准库中大部分阻塞式调用修改为协作式运行
import sys

sys.path.append('..')
import GenHeader as gen_header
import helper.Helper as helper

import setting
import random
import psutil
from multiprocessing import Queue, Pool
import logging
import time

logging.basicConfig(level=logging.DEBUG)
FREE_PROXY_SITE = [
    {
        'urls': ['http://www.66ip.cn/%s.html' % n for n in
                 ['index'] + list(range(2, 12))],
        'type': 'xpath',
        'pattern': ".//*[@id='main']/div/div[1]/table/tr[position()>1]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]',
                     'protocol': ''}
    },
    {
        'urls': ['http://www.66ip.cn/areaindex_%s/%s.html' % (m, n) for m in
                 range(1, 35) for n in range(1, 10)],
        'type': 'xpath',
        'pattern': ".//*[@id='footer']/div/table/tr[position()>1]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]',
                     'protocol': ''}
    },
    {
        'urls': ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218'],
        'type': 'xpath',
        'pattern': ".//table[@class='sortable']/tbody/tr",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
                     'protocol': ''}

    },
    {
        'urls': ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 10)],
        'type': 'xpath',
        'pattern': ".//table[@class='list']/tr",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
                     'protocol': ''}

    },
    {
        'urls': ['https://proxy-list.org/english/index.php?p=%s' % n for n in
                 range(1, 10)],
        'type': 'module',
        'moduleName': 'proxy_listPraser',
        'pattern': 'Proxy\(.+\)',
        'position': {'ip': 0, 'port': -1, 'type': -1, 'protocol': 2}

    },
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
    {
        'urls': ['http://www.kuaidaili.com/free/%s/%s/' % (m, n) for m in
                 ['inha', 'intr', 'outha', 'outtr'] for n in
                 range(1, 11)],
        'type': 'xpath',
        'pattern': ".//*[@id='list']/table/tbody/tr[position()>0]",
        'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]',
                     'protocol': './td[4]'}
    },
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
    {
        'urls': ['http://www.xicidaili.com/%s/%s' % (m, n) for m in
                 ['nn', 'nt', 'wn', 'wt'] for n in range(1, 8)],
        'type': 'xpath',
        'pattern': ".//*[@id='ip_list']/tr[position()>1]",
        'position': {'ip': './td[2]', 'port': './td[3]', 'type': './td[5]',
                     'protocol': './td[6]'}
    },
    {
        'urls': ['http://www.cnproxy.com/proxy%s.html' % i for i in
                 range(1, 11)],
        'type': 'module',
        'moduleName': 'CnproxyPraser',
        'pattern': r'<tr><td>(\d+\.\d+\.\d+\.\d+)<SCRIPT type=text/javascript>document.write\(\"\:\"(.+)\)</SCRIPT></td><td>(HTTP|SOCKS4)\s*',
        'position': {'ip': 0, 'port': 1, 'type': -1, 'protocol': 2}
    }
]


def gen_proxy():
    headers = gen_header.gen_limit_header(10)
    # wn: https代理        wt: http代理
    site = [
        {
            'urls': ['https://www.xicidaili.com/%s/%s' % (m, n) for m in [
                'wn'] for n in range(1, 2)],
            # 'type': 'xpath',
            # 'pattern': ".//*[@id='ip_list']/tr[position()>1]",
            # 'position': {'ip': './td[2]', 'port': './td[3]', 'type': './td[5]', 'protocol': './td[6]'}
        }
    ]
    # print(site[0]['urls'][0])
    if_use_proxy = helper.detect_if_need_proxy(site[0]['urls'][0])
    # print(if_use_proxy)
    result = []
    proxies = []
    for single_rul in site[0]['urls']:
        header = random.choice(headers)
        print(single_rul)
        soup = helper.send_request_get_response(url=single_rul,
                                                if_use_proxy=if_use_proxy,
                                                proxies=setting.BASIC_PROXY,
                                                header=header)
        records = soup.select('#ip_list tr:not(:first-child)')
        for single_record in records:
            ip = single_record.select('td:nth-of-type(2)')[0].string
            port = single_record.select('td:nth-of-type(3)')[0].string
            is_anonymous = single_record.select('td:nth-of-type(5)')[
                        0].string
            protocol = single_record.select('td:nth-of-type(6)')[
                        0].string

            proxies.append({
                'http': '%s:%s' % (ip, port),
                'https': '%s:%s' % (ip, port)
            })
            result.append({
                'ip': ip,
                'port': port,
                'is_anonymous': is_anonymous,
                'protocol': protocol,
            })
            # if helper.detect_if_proxy_usable(proxies):
            #     print('代理%s:%s有效' % (ip, port))
            #     result.append({
            #         'ip': ip,
            #         'port': port,
            #         'is_anonymous': is_anonymous,
            #         'protocol': protocol,
            #     })
            # else:
            #     print('代理%s:%s无效' % (ip, port))
        # print(records[0].select('td:nth-of-type(2)'))
    return result, proxies
    # print(result)
    # print(len(header))


def check_proxies_validate(proxy):
    # ip = proxy['ip']
    # port = proxy['port']
    print('check_proxies start')
    # print(proxy)
    if helper.detect_if_proxy_usable(proxy):
        print('代理 %s 有效' % proxy['http'])
    else:
        print('代理 %s 无效' % proxy['http'])


def pool_run(proxies):
    # task_list = []
    # logging.debug(psutil.cpu_count())
    print(time.time())
    p = Pool(psutil.cpu_count())
    # for single_proxy in proxies:
    #     p.apply_async(check_proxies_validate, args=(single_proxy,))
    p.apply_async(check_proxies_validate, args=(proxies[0],))
    p.apply_async(check_proxies_validate, args=(proxies[1],))
    print('Waiting for all subprocesses done...')
    start_time = time.time()
    p.close()
    p.join()
    end_time = time.time()
    print('All subprocesses done. total cost %s ms' % (end_time-start_time))
    # gevent.joinall(task_list)


def gevent_run(proxies):
    task_list = []
    # logging.debug(psutil.cpu_count())
    # print(proxies)
    # p = Pool(2)
    for single_proxy in proxies:
        task_list.append(
            gevent.spawn(check_proxies_validate, single_proxy)
        )
        # p.apply_async(check_proxies_validate, args=(single_proxy,))
    # p.apply_async(check_proxies_validate, args=(proxies[1],))
    print('Waiting for gevent done...')
    start_time = time.time()
    gevent.joinall(task_list)
    end_time = time.time()
    print('All gevent done. total cost %s ms' % (end_time-start_time))

if __name__ == '__main__':
    # tmp_proxies = [{'http': '49.83.243.248:8118', 'https': '49.83.243.248:8118'},
    #            {'http': '42.55.252.102:1133', 'https': '42.55.252.102:1133'}]
    result, tmp_proxies = gen_proxy()
    print(tmp_proxies)
    # pool_run(tmp_proxies)
    gevent_run(tmp_proxies)