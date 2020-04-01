#! /usr/bin/env python3
# -*- coding:utf-8 -*-
'''
从不同的代理网站，获取代理
'''

import self.SelfEnum as self_enum
import setting
import re
import base64
import logging
logging.basicConfig(level=logging.DEBUG)

def extra_data_from_page_xicidaili(soup):
    '''
    筛选protocol（HTTP/HTTPS，socks在gen_proxy中处理）和proxy_type（透明/匿名）
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
        if self_enum.ProxyType.All in setting.proxy_filter['type'] and \
                self_enum.ProtocolType.ALL in setting.proxy_filter['protocol']:
            result.append({'ip': ip, 'port': port, 'protocol': protocol,
                           'type': is_anonymous})
            continue
        # 如果期望获得透明，但获得的proxy不是透明，跳过
        if self_enum.ProxyType.Transparent in setting.proxy_filter['type']:
            if is_anonymous != 'TRANS':
                continue
        # 如果期望获得高匿，但获得的不是高匿，跳过
        if self_enum.ProxyType.Anonymous in setting.proxy_filter['type'] or \
                self_enum.ProxyType.High16yun in setting.proxy_filter['type']:
            if is_anonymous != 'HIGH_ANON':
                continue
        # 如果期望获得HTTP，但获得的proxy不是HTTP，跳过
        if self_enum.ProtocolType.HTTP in setting.proxy_filter['protocol']:
            if protocol != 'HTTP':
                continue
        # 如果期望获得HTTPS，但获得的proxy不是HTTPS，跳过
        if self_enum.ProtocolType.HTTPS in setting.proxy_filter['protocol']:
            if protocol != 'HTTPS':
                continue
        # proxies.append({
        #     'http': '%s:%s' % (ip, port),
        #     'https': '%s:%s' % (ip, port)
        # })
        result.append({'ip': ip, 'port': port, 'protocol': protocol,
                       'type': is_anonymous})
    return result


def extra_data_from_page_kuaidaili(soup):
    '''
    proxy-type（透明/匿名）和protocol筛选在上级完成。无country筛选
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
    此处过来国家和protocol。proxy_type（透明/匿名）在gen_proxy中过滤
    :param soup: 读取页面的html内容
    :return: list，当前页面所有proxy记录
    '''
    # print(soup.string)
    result = []
    records = soup.select('div.table>ul')
    for single_record in records:
        raw_country = single_record.select(
            'li.country-city>div>span.country>span.country-code>span.name')[
            0].string
        country = raw_country.split(' ')[1]
        # 如果没有All，那么需要检测国家是否在setting.proxy_filter.country中
        if self_enum.Country.All not in setting.proxy_filter['country']:
            # 检测country是否在enum中
            if country not in self_enum.Country.__members__:
                logging.debug('%s未在enum中定义' % country)
                continue
            if self_enum.Country[country] \
                    not in setting.proxy_filter['country']:
                continue

        # 如果是HTTPS，包含在<strong>HTTPS</strong>中；如果是HTTP，直接在li下
        raw_protocol = single_record.select('li.https>strong')
        if len(raw_protocol) > 0:
            protocol = 'HTTPS'
        else:
            protocol = 'HTTP'
        # 根据setting，筛选protocol
        if self_enum.ProtocolType.ALL not in setting.proxy_filter['protocol']:
            # if self_enum.ProtocolType.HTTP \
            #         not in setting.proxy_filter['protocol'] \
            #         and protocol == 'HTTP':
            #     continue
            # if self_enum.ProtocolType.HTTPS \
            #         not in setting.proxy_filter['protocol'] \
            #         and protocol == 'HTTPS':
            #     continue
            if self_enum.ProtocolType[protocol] \
                    not in setting.proxy_filter['protocol']:
                continue
        # 将Proxy('MjAzLjE3Ni4xMzMuMzg6ODA4MA==')变成['1.1.1.1', '8080']的格式
        raw_ip = single_record.select('li.proxy')[0].get_text()
        ip_base64 = re.match(r'Proxy\(\'(.*)\'\)', raw_ip).group(1)
        ip_str = base64.b64decode(ip_base64).decode('utf-8').split(':')
        ip = ip_str[0]
        port = ip_str[1]

        raw_proxy_type = single_record.select('li.type')[0].string
        # print('国家:%s , ip: %s, port: %s, 协议:%s, 类型:%s' % (country, ip, port,
        #                                                   protocol, type))
        # print(raw_type)
        if raw_proxy_type == 'Transparent':
            proxy_type = 'TRANS'
        elif raw_proxy_type == 'Elite':
            proxy_type = 'HIGN_ANON'
        elif raw_proxy_type == 'Anonymous':
            proxy_type = 'ANON'
        else:
            print('未知代理类型 %s' % raw_proxy_type)
            continue
        # print(type)
        result.append({'ip': ip, 'port': port, 'protocol': protocol,
                       'type': proxy_type})
    return result


def extra_data_from_page_hidemy(soup):
    '''
    筛选protocol/type/country
    :param soup: 读取页面的html内容
    :return: list，当前页面所有proxy记录
    '''
    result = []
    records = soup.select('table.proxy__t>tbody>tr')
    for single_record in records:
        ip = single_record.select('td:nth-of-type(1)')[0].string
        port = single_record.select('td:nth-of-type(2)')[0].string
        country = single_record.select('td:nth-of-type(3)>div')[0].string
        protocol = single_record.select('td:nth-of-type(5)')[0].string
        raw_type =single_record.select('td:nth-of-type(6)')[0].string
        print('%s,%s,%s,%s,%s' % (ip, port, country, protocol, raw_type))