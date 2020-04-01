#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import sys
sys.path.append('../..')
import pytest
import helper.PreFilter as pre_filter
import setting
import self.SelfEnum as self_enum

@pytest.mark.xicidaili
class Test_pre_filter_xicidaili:
    # xici不支持socks，只支持http/https
    def test_all(self):
        '''
        ALL should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.ALL]
        assert pre_filter.pre_filter_xicidaili() == True

    def test_http(self):
        '''
        http should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.HTTP]
        assert pre_filter.pre_filter_xicidaili() == True

    def test_socks(self):
        '''
        socks should return False
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.SOCKS]
        assert pre_filter.pre_filter_xicidaili() == False

    def test_socks_all(self):
        '''
        ALL+Sock should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.SOCKS,
                                            self_enum.ProtocolType.ALL]
        assert pre_filter.pre_filter_xicidaili() == True

    def test_http_socks(self):
        '''
        http+sock should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.SOCKS,
                                            self_enum.ProtocolType.HTTP]
        assert pre_filter.pre_filter_xicidaili() == True


@pytest.mark.kuaidaili
class Test_pre_filter_kuaidaili:
    # kuaidaili只支持HTTP，无国家
    def test_all(self):
        '''
        ALL should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.ALL]
        assert pre_filter.pre_filter_kuaidaili() == True

    def test_http(self):
        '''
        http should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.HTTP]
        assert pre_filter.pre_filter_kuaidaili() == True

    def test_https(self):
        '''
        https should return false
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.HTTPS]
        assert pre_filter.pre_filter_kuaidaili() == False

    def test_socks(self):
        '''
        socks should return false
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.SOCKS]
        assert pre_filter.pre_filter_kuaidaili() == False

    def test_all_socks(self):
        '''
        ALL+sock should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.ALL,
                                            self_enum.ProtocolType.SOCKS]
        assert pre_filter.pre_filter_kuaidaili() == True

    def test_all_https(self):
        '''
        ALL+http should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.ALL,
                                            self_enum.ProtocolType.HTTPS]
        assert pre_filter.pre_filter_kuaidaili() == True

    def test_all_http(self):
        '''
        ALL+http should return true
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.ALL,
                                            self_enum.ProtocolType.HTTPS]
        assert pre_filter.pre_filter_kuaidaili() == True

    def test_https_socks5(self):
        '''
        http+sock5 should return false
        '''
        setting.proxy_filter['protocol'] = [self_enum.ProtocolType.SOCKS5,
                                            self_enum.ProtocolType.HTTPS]
        assert pre_filter.pre_filter_kuaidaili() == False