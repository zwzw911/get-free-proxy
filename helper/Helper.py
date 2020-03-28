#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup
import chardet
import generator.GenHeader as gen_header
import self.SelfException as self_exception

def match_expect_type(value,expect_type):
    '''
    :param value:  待检查的值
    :param expect_type:    字符，期望的类型
    :return: Boolean
    '''
    return expect_type in str(type(value))


def val_in_enum(val,enum):
    '''
    检测val是否是enum定义的值
    :param val: 待检测的enum值
    :param enum: enum类型
    :return: boolean
    '''
    return val in enum


def detect_if_need_proxy(url):
    header = gen_header.gen_limit_header(1)[0]
    print(header)
    try:
        r = requests.get(url, headers=header, timeout=5)
    except requests.exceptions.ConnectTimeout as e:
        print('不通过代理发起的请求超时，需要使用代理')
        return True
    return False


def detect_if_proxy_usable(proxies):
    header = gen_header.gen_limit_header(1)[0]
    # print(header)
    try:
        r = requests.get(url='https://www.baidu.com', headers=header,
                         proxies=proxies, timeout=5)
    except requests.exceptions.ConnectionError as e:
        # print('代理无效')
        return False
    except requests.exceptions.ConnectTimeout as e:
        # print('代理无效')
        return False
    except requests.exceptions.ProxyError as e:
        return False
    return True


def send_request_get_response(*, url, if_use_proxy, proxies, header):
    '''
    :param url:
    :param if_use_proxy:  boolean
    :param proxies: dict，如果if_need_proxy为true，传入代理
    :param header: request的header
    :return: root soup
    '''

    # logging.debug(header)
    if if_use_proxy:
        r = requests.get(url, headers=header, proxies=proxies,
                         timeout=5)
    else:
        r = requests.get(url, headers=header, timeout=2)

    if r.status_code != 200:
        print('错误代码 %s' % r.status_code)
        raise self_exception.ResponseException(r.status_code)

    # raise e.ResponseException(200)
    # logging.debug(chardet.detect(r.content)['encoding'])
    # logging.debug(r.text)
    encoding = chardet.detect(r.content)['encoding']
    if encoding == 'utf-8':
        soup = BeautifulSoup(r.text, 'lxml')
    else:
        soup = BeautifulSoup(r.text, 'lxml', from_encoding=encoding)

    return soup


if __name__ == '__main__':
    pass