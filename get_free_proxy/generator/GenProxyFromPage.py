#! /usr/bin/env python3
# -*- coding:utf-8 -*-
'''
从不同的代理网站，获取代理
'''

# from src import self as self_enum, setting
import get_free_proxy.self.SelfEnum as gfp_self_enum
# import get_free_proxy.setting.Setting as gfp_setting
import re
import base64
import logging

logging.basicConfig(level=logging.DEBUG)


def extra_data_from_page_xicidaili(r, gfp_setting):
    '''
    筛选protocol（HTTP/HTTPS，socks在gen_proxy中处理）和proxy_type（透明/匿名）
    :param r: requests-html
    :return: list，当前页面所有proxy记录
    '''
    # print(r.html)
    records = r.html.find('#ip_list tr:not(:first-child)')
    result = []
    # logging.info(gfp_setting.proxy_type)
    # logging.info(gfp_setting.protocol)
    for single_record in records:
        # print(single_record)
        ip = single_record.find('td:nth-of-type(2)')[0].text
        port = single_record.find('td:nth-of-type(3)')[0].text
        is_anonymous = single_record.find('td:nth-of-type(5)')[
            0].text
        is_anonymous = 'TRANS' if is_anonymous == '透明' else 'HIGH_ANON'
        protocol = single_record.find('td:nth-of-type(6)')[
            0].text.upper()
        # # 期望是所有，直接添加
        # if gfp_self_enum.ProxyType.All in gfp_setting.proxy_type and \
        #         gfp_self_enum.ProtocolType.ALL in gfp_setting.protocol:
        #     result.append({'ip': ip, 'port': port, 'protocol': protocol,
        #                    'proxy_type': is_anonymous})
        #     continue
        # is_anonymous = 'test'
        if is_anonymous not in gfp_self_enum.ProxyType.__members__:
            # print('test')
            continue
        if gfp_self_enum.ProxyType[is_anonymous] not in gfp_setting.proxy_type:
            continue
        # # 如果期望获得透明，但获得的proxy不是透明，跳过
        # if gfp_self_enum.ProxyType.TRANS in gfp_setting.proxy_type:
        #     if is_anonymous != 'TRANS':
        #         continue
        # # 如果期望获得高匿，但获得的不是高匿，跳过
        # if gfp_self_enum.ProxyType.ANON in gfp_setting.proxy_type or \
        #         gfp_self_enum.ProxyType.HIGH_ANON in gfp_setting.proxy_type:
        #     if is_anonymous != 'HIGH_ANON':
        #         continue
        # 如果期望获得HTTP，但获得的proxy不是HTTP，跳过
        # logging.info(gfp_self_enum.ProtocolType[protocol])
        if gfp_self_enum.ProtocolType[protocol] not in gfp_setting.protocol:
            continue
        # if gfp_self_enum.ProtocolType.HTTP in gfp_setting.protocol:
        #     if protocol != 'HTTP':
        #         continue
        # # 如果期望获得HTTPS，但获得的proxy不是HTTPS，跳过
        # if gfp_self_enum.ProtocolType.HTTPS in gfp_setting.protocol:
        #     if protocol != 'HTTPS':
        #         continue
        # logging.info('get result ip %s' % ip)
        # proxies.append({
        #     'http': '%s:%s' % (ip, port),
        #     'https': '%s:%s' % (ip, port)
        # })
        result.append({'ip': ip, 'port': port, 'protocol': protocol,
                       'proxy_type': is_anonymous})
    # logging.info('extra_data_from_page_xicidaili result %s' % result)
    return result


def extra_data_from_page_kuaidaili(r, gfp_setting):
    '''
    proxy-type（透明/匿名）和protocol筛选在上级完成。无country筛选
    :param r: requests-html
    :return: list，当前页面所有proxy记录
    '''
    records = r.html.find('tbody>tr')
    result = []
    for single_record in records:
        ip = single_record.find('td[data-title=IP]')[0].text
        port = single_record.find('td[data-title=PORT]')[0].text
        is_anonymous = single_record.find('td[data-title=匿名度]')[
            0].text
        is_anonymous = 'TRANS' if is_anonymous == '透明' else 'HIGH_ANON'
        protocol = single_record.find('td[data-title=类型]')[
            0].text.upper()
        result.append({'ip': ip, 'port': port, 'protocol': protocol,
                       'proxy_type': is_anonymous})
    return result


def extra_data_from_page_proxylist(r, gfp_setting):
    '''
    此处过来国家和protocol。proxy_type（透明/匿名）在gen_proxy中过滤
    :param r: requests-html
    :return: list，当前页面所有proxy记录
    '''
    # print(r.string)
    result = []
    records = r.html.find('div.table>ul')
    # print(gfp_setting.protocol)
    # print(gfp_setting.proxy_type)
    # print(gfp_setting.country)
    for single_record in records:
        # print(single_record)
        raw_country = single_record.find(
            'li.country-city>div>span.country>span.country-code>span.name')[
            0].text
        country = raw_country.split(' ')[1]

        if country not in gfp_self_enum.Country.__members__:
            logging.warning('%s未在enum中定义' % country)
            continue
        # 如果没有All，那么需要检测国家是否在setting.proxy_filter.country中
        if gfp_self_enum.Country.All not in gfp_setting.country:
            # 检测country是否在enum中
            if gfp_self_enum.Country[country] not in gfp_setting.country:
                continue

        # 如果是HTTPS，包含在<strong>HTTPS</strong>中；如果是HTTP，直接在li下
        raw_protocol = single_record.find('li.https>strong')
        if len(raw_protocol) > 0:
            protocol = 'HTTPS'
        else:
            protocol = 'HTTP'

        # 根据setting，筛选protocol
        if gfp_self_enum.ProtocolType.All not in gfp_setting.protocol:
            # if self_enum.ProtocolType.HTTP \
            #         not in setting.proxy_filter['protocol'] \
            #         and protocol == 'HTTP':
            #     continue
            # if self_enum.ProtocolType.HTTPS \
            #         not in setting.proxy_filter['protocol'] \
            #         and protocol == 'HTTPS':
            #     continue
            if gfp_self_enum.ProtocolType[protocol] \
                    not in gfp_setting.protocol:
                continue
        # 将Proxy('MjAzLjE3Ni4xMzMuMzg6ODA4MA==')变成['1.1.1.1', '8080']的格式
        raw_ip = single_record.find('li.proxy')[0].text
        # print(raw_ip)
        ip_base64 = re.match(r'Proxy\(\'(.*)\'\)', raw_ip).group(1)
        ip_str = base64.b64decode(ip_base64).decode('utf-8').split(':')
        ip = ip_str[0]
        port = ip_str[1]

        raw_proxy_type = single_record.find('li.type')[0].text
        # print('国家:%s , ip: %s, port: %s, 协议:%s, 类型:%s' % (country, ip, port,
        #                                                   protocol, type))
        # print(raw_type)
        if raw_proxy_type == 'Transparent':
            proxy_type = 'TRANS'
        elif raw_proxy_type == 'Elite':
            proxy_type = 'HIGH_ANON'
        elif raw_proxy_type == 'Anonymous':
            proxy_type = 'ANON'
        else:
            print('未知代理类型 %s' % raw_proxy_type)
            continue
        if gfp_self_enum.ProxyType[proxy_type] not in gfp_setting.proxy_type:
            continue

        # print(proxy_type)
        result.append({'ip': ip, 'port': port, 'protocol': protocol,
                       'proxy_type': proxy_type})
    return result


def extra_data_from_page_hidemy(r, gfp_setting):
    '''
    筛选protocol/type/country
    :param r: requests-html
    :return: list，当前页面所有proxy记录
    '''
    result = []
    records = r.html.find('table.proxy__t>tbody>tr')
    for single_record in records:
        ip = single_record.find('td:nth-of-type(1)')[0].string
        port = single_record.find('td:nth-of-type(2)')[0].string
        country = single_record.find('td:nth-of-type(3)>div')[0].string
        protocol = single_record.find('td:nth-of-type(5)')[0].string
        raw_type = single_record.find('td:nth-of-type(6)')[0].string
        print('%s,%s,%s,%s,%s' % (ip, port, country, protocol, raw_type))
