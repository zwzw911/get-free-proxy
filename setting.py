#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import self.SelfEnum as self_enum
BASIC_PROXY = {
    'http': '87.254.212.121:8080',
    'https': '87.254.212.121:8080'
}

proxy_filter = {
    'type': [self_enum.ProxyType.All],
    'protocol': [self_enum.ProtocolType.HTTP],
    # https://proxy-list.org中代理来自全球，使用country进行过滤
    'country': [self_enum.Country.China],
}
# proxy_type = self_enum.ProxyType.High16yun
#
# proxy_country
