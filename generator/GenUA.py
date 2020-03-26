#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
sys.path.append('..')
import requests
from bs4 import BeautifulSoup
import logging
import random
import chardet
from datetime import datetime

# from self.SelfError import ResponseException
import self.SelfError as e
import self.SelfEnum as self_enum
# import self.SelfError
import helper.Helper as helper

logging.basicConfig(level=logging.DEBUG)
# 6.0 = Vista   6.1=win7    6.2=win8   6.3=win8.1   10 = win10
WIN_VER = ['Windows NT 6.0', 'Windows NT 6.1', 'Windows NT 6.2',
           'Windows NT 6.3', 'Windows NT 10.0']


def generate_firefox_ua(num=None):
    '''
    生成所有firefox的UA，供选择
    :param num: 生成header的个数。如果是None，返回所有
    :return: list
    '''
    firefox_ver = [float(x) for x in range(56, 74)]
    firefox_header = ['Mozilla/5.0 (%s; Win64; x64; rv:%s) \
Gecko/20100101 Firefox/%s' % (win_ver, f_ver, f_ver)
                      for win_ver in WIN_VER for f_ver in firefox_ver]
    if num is not None:
        # 如果只需要返回一个，直接生成
        if num == 1:
            return ['Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) \
Gecko/20100101 Firefox/74.0']
        if len(firefox_header) > num:
            return random.sample(firefox_header, num)

    return firefox_header
    # if
    # else:

    # logging.debug(firefox_header)





def generate_chrome_url_base_on_type(*,
                                     os_type={self_enum.OsType.Win64},
                                     chrome_type={self_enum.ChromeType.Stable}):
    '''
    :param os_type: set,
    :param chrome_type: set,
    :return: set，包含需要获取版本的url
    '''
    # 检测传入参数的类型
    if not helper.match_expect_type(os_type, 'set'):
        raise ValueError('generate_chrome_url_base_on_type的参数os_type，不是set')
    if not helper.match_expect_type(chrome_type, 'set'):
        raise ValueError('generate_chrome_url_base_on_type的参数chrome_type，不是set')
    # 检测传入参数是否符合enum定义
    for single in os_type:
        if single not in self_enum.OsType:
            raise ValueError(
                'generate_chrome_url_base_on_type的参数os_type，元素不是OsType')

    for single in chrome_type:
        if single not in self_enum.ChromeType:
            raise ValueError('generate_chrome_url_base_on_type的参数chrome_type\
,元素不是ChromeType')

    if self_enum.ChromeType.All in chrome_type:
        chrome_type = {self_enum.ChromeType.Stable, self_enum.ChromeType.Beta,
                       self_enum.ChromeType.Dev, self_enum.ChromeType.Canary}
    if self_enum.OsType.All in os_type:
        os_type = {self_enum.OsType.Win32, self_enum.OsType.Win64}

    # enum对应的字符
    os_dict = {
        self_enum.OsType.Win32: 'chrome32win',
        self_enum.OsType.Win64: 'chrome64win'
    }

    part_url = ''
    base_url = 'https://www.chromedownloads.net/'
    result = []
    for single_os_type in os_type:
        for single in chrome_type:
            part_url = os_dict[single_os_type] + '-' + single.name.lower()
            result.append(base_url + part_url)

    return result


def get_chrome_ver(*, url, max_release_years, if_use_proxy):
    '''
    :param url: 获取chrome版本的url
    :param max_release_years: 版本距今最长年数
    :param if_use_proxy: 是否使用代理
    :return: set
    '''
    chrome_ver = set({})


    current_year = datetime.now().year
    records = soup.select('div.download_content>ul.fix>'
                          'li[class!=divide-line]')

    for single_record in records:
        version_element_list = single_record.select('span.version_title>a')
        release_data_element_list = single_record.select(
            'span.release_date')
        # 第一个li是标题，需要忽略
        if len(version_element_list) == 0:
            continue
        # 判断版本时间
        version_release_year = \
            int(release_data_element_list[0].string.split('-')[0])
        if current_year - version_release_year > max_release_years:
            continue

        chrome_ver.add(version_element_list[0].string.split('_')[3])
    return chrome_ver


def generate_chrome_ua(*, max_release_years=2,
                       os_type={self_enum.OsType.Win64},
                       chrome_type={self_enum.ChromeType.Stable}):
    '''
    :param max_release_years:
        int，距离现在最大时间（年为单位）。
        比如现在是2020，这取的chrome版本不能遭遇2018，避免取到太老的版本
    :param os_type: set,
    :param chrome_type: set,
    :return: list，包含需要获取版本的UA
    '''
    try:
        version_url = generate_chrome_url_base_on_type(
            os_type=os_type,
            chrome_type=chrome_type)
    except ValueError as e:
        # print('generate_chrome_header调用generate_chrome_url_base_on_type'
        #       '，传入的参数必须是set')
        print(e)
        return

    # 检测是否需要代理，如果需要，设置代理
    if_use_proxy = helper.detect_if_need_proxy(version_url[0])

    chrome_ver = set({})
    for single_url in version_url:
        tmp_chrome_ver = get_chrome_ver(url=single_url,
                                        max_release_years=max_release_years,
                                        if_use_proxy=if_use_proxy)
        # logging.debug(tmp_chrome_ver)
        # 获得的version加入chrome_ver
        chrome_ver = chrome_ver | tmp_chrome_ver
    # logging.debug(chrome_ver)
    if len(os_type) == 2:
        os_bit = {32, 64}
    elif os_type == self_enum.OsType.Win32:
        os_bit = {32}
    else:
        os_bit = {64}

    result = ['Mozilla/5.0 (%s; WOW%s) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/%s Safari/537.36' % (winver, osbit, chromever)
              for osbit in os_bit
              for winver in WIN_VER
              for chromever in chrome_ver
              ]
    return result


if __name__ == '__main__':
    try:
        generate_chrome_ua(chrome_type={self_enum.ChromeType.Stable,
                                        self_enum.ChromeType.Beta})
    except e.ResponseException as e:
        print(e)

# USER_AGENT=[
#
# ]
# FREE_PROXY_SITE = [
#     {
#         'urls': ['http://www.xicidaili.com/%s/%s' % (m, n) for m in
#                  ['nn', 'nt', 'wn', 'wt'] for n in range(1, 8)],
#         'type': 'bs4',
#         'pattern': "#ip_list>tr",
#         'position': {'ip': './td[2]', 'port': './td[3]', 'type': './td[5]',
#                      'protocol': './td[6]'}
#     },
# ]
#
# def getProxyIp():
#     requests.get(url=)
