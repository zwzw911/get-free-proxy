#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import sys
sys.path.append('..')

import generator.GenUA as gen_ua
import self.SelfEnum as self_enum
# import test.TestData as test_data

def gen_header():

    ua = gen_ua.generate_firefox_ua()+gen_ua.generate_chrome_ua(
        os_type={self_enum.OsType.All}, chrome_type={self_enum.ChromeType.All})
    header = []
    for single_ua in ua:
        header.append({
            'User-Agent': single_ua,
            'Accept': 'text/html, application/xhtml+xml, application/xml;\
q = 0.9, image/webp, image/apng, */*;\
q = 0.8, application/signed-exchange;v = b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN, zh;q = 0.9',
            'Connection': 'keep-alive'
        })

    return header


def gen_limit_header(num=None):

    ua = gen_ua.generate_firefox_ua(num)
    header = []
    for single_ua in ua:
        header.append({
            'User-Agent': single_ua,
            'Accept': 'text/html, application/xhtml+xml, application/xml;\
q = 0.9, image/webp, image/apng, */*;\
q = 0.8, application/signed-exchange;v = b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN, zh;q = 0.9',
            'Connection': 'keep-alive'
        })

    return header


if __name__ == '__main__':
    print(gen_limit_header())
