#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import requests
from multiprocessing import Queue, Pool

header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) \
Gecko/20100101 Firefox/74.0',
            'Accept': 'text/html, application/xhtml+xml, application/xml;\
q = 0.9, image/webp, image/apng, */*;\
q = 0.8, application/signed-exchange;v = b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN, zh;q = 0.9',
            'Connection': 'keep-alive'
        }


def check_proxies_validate(proxy):
    # ip = proxy['ip']
    # port = proxy['port']
    print('check_proxies start')
    try:
        r = requests.get(url='https://www.baidu.com', headers=header,
                         proxies=proxy, timeout=5)
    except requests.exceptions.ConnectTimeout as e:
        print('proxy %s is invalid' % proxy['http'])
        return False
    print('proxy %s is valid' % proxy['http'])
    return True




if __name__ == '__main__':
    proxies = [{'http': '49.83.243.248:8118', 'https': '49.83.243.248:8118'},
               {'http': '42.55.252.102:1133', 'https': '42.55.252.102:1133'}]
    # result, proxies = gen_proxy()
    # task_list = []
    # logging.debug(psutil.cpu_count())
    # print(proxies)
    p = Pool(2)
    # for single_proxy in proxies:
        # task_list.append(
        #     gevent.spawn(check_proxies_validate,single_proxy)
        # )
    p.apply_async(check_proxies_validate, args=(proxies[0],))
    p.apply_async(check_proxies_validate, args=(proxies[1],))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    # gevent.joinall(task_list)