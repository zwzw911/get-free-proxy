#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import tempfile
import os

import get_free_proxy.self.SelfEnum as gfp_self_enum

import gen_browser_header.helper.Helper as gbh_helper


class GfpSetting(object):
    '''
    get-free-proxy的设置:
    _proxy_type: 获得的代理的类型：透明、匿名、高匿
    _protocol: 代理的协议：http/https/sock
    _country: 代理所在的国家
    _storage_type: 结果存储类型， 默认file
    _mysql： 如果_storage_type选择MYSQL，那么MYSQL连接的设置
    _redis'：如果_storage_type选择REDIS，那么REDIS连接的设置
    _result_file_path：如果_storage_type选择FILE，那么FILE的路径
    _valid_time_in_db: 如果选择结果存储在db，最大保存时间（免费代理不稳定，可能过时）
    _site_max_page_no: 在免费代理网站上取几页数据
    _site：免费代理网站的url地址
    '''
    __slots__ = ('_proxy_type', '_protocol', '_country', '_storage_type',
                 '_mysql', '_redis', '_result_file_path', '_valid_time_in_db',
                 '_site_max_page_no', '_raw_site', '_site')

    def _generate_site(self, enumset_site, enumset_protocol, int_site_max_page_no):
        '''
        site是根据_protocol（xici)，以及_site_max_page_no生成的，其中任意一个参数变化，
        都要重新生成self.site
        :return:list。直接赋值给self._site
        '''
        result = []
        # xici
        if gfp_self_enum.SupportedWeb.Xici in enumset_site:
            xici_tmp = []
            # print(enumset_protocol)
            if gfp_self_enum.ProtocolType.HTTP in enumset_protocol:
                xici_tmp.append('wt')
            if gfp_self_enum.ProtocolType.HTTPS in enumset_protocol:
                xici_tmp.append('wn')
            if len(xici_tmp) > 0:
                result.append(
                    {
                        # wn: https代理        wt: http代理    透明/高匿混合在同一页面
                        # socks代理验证时间太长，所以不采用
                        'urls': ['https://www.xicidaili.com/%s/%s' % (m, n) for m in xici_tmp
                                 for n in range(1, int_site_max_page_no)],
                        'enum_site': gfp_self_enum.SupportedWeb.Xici,
                        'need_proxy': False,
                        'force_render':False
                    },
                )
        # kuai
        if gfp_self_enum.SupportedWeb.Kuai in enumset_site:
            # kuai只支持HTTP
            if gfp_self_enum.ProtocolType.HTTP in enumset_protocol:
                result.append(
                    {
                        # inha：国内高匿   intr：国内透明
                        # kuaidaili只有http代理
                        'urls': ['https://www.kuaidaili.com/free/%s/%s' % (m, n) for m in
                                 ['inha', 'intr'] for n in range(1, int_site_max_page_no)],
                        'enum_site': gfp_self_enum.SupportedWeb.Kuai,
                        'need_proxy': False,
                        'force_render': False
                    },
                )
        # proxy-list
        if gfp_self_enum.SupportedWeb.Proxylist in enumset_site:
            if gfp_self_enum.ProtocolType.HTTP in enumset_protocol or \
                    gfp_self_enum.ProtocolType.HTTPS in enumset_protocol:
                result.append(
                    {
                        # proxy-list只有http/https代理
                        'urls': ['https://proxy-list.org/english/index.php?p=%s' % m for m
                                 in range(1, int_site_max_page_no)],
                        'enum_site': gfp_self_enum.SupportedWeb.Proxylist,
                        'need_proxy': False,
                        'force_render': False
                    },
                )
        # hidemy
        if gfp_self_enum.SupportedWeb.Hidemy in enumset_site:
            result.append(
                {
                    # hidemy.name支持所有protocol，2种type，和国家
                    'urls': ['https://hidemy.name/en/proxy-list/?start=%s#list' %
                             str((m - 1) * 64) if m > 1 else
                             'https://hidemy.name/en/proxy-list/?start=1#list'
                             for m in range(1, int_site_max_page_no)],
                    'enum_site': gfp_self_enum.SupportedWeb.Hidemy,
                    'need_proxy': False,
                    'force_render': False
                }
            )

        return result

    def __init__(self):
        self._proxy_type = {gfp_self_enum.ProxyType.HIGH_ANON}
        self._protocol = {gfp_self_enum.ProtocolType.HTTP,
                          gfp_self_enum.ProtocolType.HTTPS}
        self._country = {gfp_self_enum.Country.China}
        self._storage_type = {gfp_self_enum.StorageType.File}
        self._mysql = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'pwd': '1234',
            'db_name': 'db_proxy',
            'tbl_name': 'tbl_proxy',
            'charset': 'utf8mb4'
        }
        self._redis = {
            'host': '127.0.0.1',
            'port': 6379,
            'db': 0,  # 0~15
            'pwd': None
        }
        self._result_file_path = os.path.join(tempfile.gettempdir(), 'result.json')
        self._valid_time_in_db = 86400
        self._site_max_page_no = 5

        self._raw_site = {gfp_self_enum.SupportedWeb.Xici,
                          gfp_self_enum.SupportedWeb.Kuai,
                          gfp_self_enum.SupportedWeb.Proxylist,
                          gfp_self_enum.SupportedWeb.Hidemy
                          }
        self._site = self._generate_site(enumset_site=self._raw_site,
                                         enumset_protocol=self.protocol,
                                         int_site_max_page_no=self._site_max_page_no
                                         )

    @property
    def proxy_type(self):
        return self._proxy_type

    @proxy_type.setter
    def proxy_type(self, value):
        r = gbh_helper.enum_set_check(value=value, enum_type=gfp_self_enum.ProxyType)
        if r is None:
            return
        else:
            self._proxy_type = r

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        r = gbh_helper.enum_set_check(value=value, enum_type=gfp_self_enum.ProtocolType)
        if r is None:
            return
        else:
            self._protocol = r
            self._site = self._generate_site(enumset_site=self._raw_site,
                                             enumset_protocol=self._protocol,
                                             int_site_max_page_no=self._site_max_page_no)

    @property
    def country(self):
        return self._country

    @country.setter
    # country太多，All无需替换成非All成员
    def country(self, value):
        r = gbh_helper.enum_set_check(value=value, enum_type=gfp_self_enum.Country,
                                      replace=False)
        if r is None:
            return
        else:
            self._country = r

    @property
    def storage_type(self):
        return self._storage_type

    @storage_type.setter
    def storage_type(self, value):
        r = gbh_helper.enum_set_check(value=value, enum_type=gfp_self_enum.StorageType)
        if r is None:
            return
        else:
            self._storage_type = r

    @property
    def result_file_path(self):
        return self._result_file_path

    @result_file_path.setter
    def result_file_path(self, value):
        base_dir = os.path.dirname(value)
        if not os.path.exists(base_dir):
            raise ValueError('目录%s不存在，无法创建文件保存结果' % base_dir)

    @property
    def mysql(self):
        return self._mysql

    @mysql.setter
    def mysql(self, value):
        # 偷懒，不检测
        self._mysql = value

    @property
    def redis(self):
        return self._redis

    @redis.setter
    def redis(self, value):
        # 偷懒，不检测
        self._redis = value

    @property
    def valid_time_in_db(self):
        return self._valid_time_in_db

    @valid_time_in_db.setter
    def valid_time_in_db(self, value):
        if not gbh_helper.match_expect_type(value, 'int'):
            raise ValueError('valid_time_in_db的值必须是整数')
        if value < 300 or value > 86400 * 5:
            raise ValueError('valid_time_in_db的值必须在300到86400×5之间')
        self._valid_time_in_db = value

    @property
    def site_max_page_no(self):
        return self._site_max_page_no

    @site_max_page_no.setter
    def site_max_page_no(self, value):
        if not gbh_helper.match_expect_type(value, 'int'):
            raise ValueError('site_max_page_no的值必须是整数')
        if value < 1 or value > 10:
            raise ValueError('site_max_page_no的值必须在1到9之间')
        # 实际使用列表表达式生成url，因此site_max_page_no要+1，符合感受
        self._site_max_page_no = value+1

        self._site = self._generate_site(enumset_site=self._raw_site,
                                         enumset_protocol=self._protocol,
                                         int_site_max_page_no=self._site_max_page_no)
    @property
    def raw_site(self):
        return self._raw_sitesit

    @raw_site.setter
    def raw_site(self, value):
        r = gbh_helper.enum_set_check(value=value, enum_type=gfp_self_enum.SupportedWeb)
        if r is None:
            return
        else:
            self._raw_site = r
            self._site = self._generate_site(enumset_site=self._raw_site,
                                             enumset_protocol=self._protocol,
                                             int_site_max_page_no=self._site_max_page_no)

    @property
    def site(self):
        return self._site

    # @site.setter
    # def site(self, value):
    #     # set
    #     if not gbh_helper.match_expect_type(value, 'set'):
    #         raise ValueError('site必须是set')
    #     # 当前仅仅支持https://www.xicidaili.com/https://www.kuaidaili.com/https://hidemy.name/
    #     # valid_url = set('https://www.xicidaili.com','https://www.kuaidaili.com','https://hidemy.name')
    #     r = gbh_helper.enum_set_check(value, gfp_self_enum.SupportedWeb)
    #     if r is None:
    #         return
    #
    #     # 清空数组，根据输入重新赋值，所有url默认无需使用代理
    #     self._site = []
    #     if gfp_self_enum.SupportedWeb.Xici in r:
    #         xici_tmp = []
    #         if gfp_self_enum.ProtocolType.HTTP in self._protocol:
    #             xici_tmp.append('wt')
    #         if gfp_self_enum.ProtocolType.HTTPS in self._protocol:
    #             xici_tmp.append('wn')
    #         if len(xici_tmp) > 0:
    #             self._site.append(
    #                 {
    #                     # wn: https代理        wt: http代理    透明/高匿混合在同一页面
    #                     # socks代理验证时间太长，所以不采用
    #                     'urls': ['https://www.xicidaili.com/%s/%s' % (m, n) for m in [
    #                         'wn', 'wt'] for n in range(1, self._site_max_page_no)],
    #                     'enum_site': gfp_self_enum.SupportedWeb.Xici,
    #                     'need_proxy': False
    #                 }
    #             )
    #     if gfp_self_enum.SupportedWeb.Kuai in r:
    #         self._site.append(
    #             {
    #                 # inha：国内高匿   intr：国内透明
    #                 # kuaidaili只有http代理
    #                 'urls': ['https://www.kuaidaili.com/free/%s/%s' % (m, n) for m in
    #                          ['inha', 'intr'] for n in range(1, self._site_max_page_no)],
    #                 'enum_site': gfp_self_enum.SupportedWeb.Kuai,
    #                 'need_proxy': False
    #             }
    #         )
    #     if gfp_self_enum.SupportedWeb.Proxylist in r:
    #         self._site.append(
    #             {
    #                 # proxy-list只有http/https代理
    #                 'urls': ['https://proxy-list.org/english/index.php?p=%s' % m for m
    #                          in range(1, self._site_max_page_no)],
    #                 'enum_site': gfp_self_enum.SupportedWeb.Proxylist,
    #                 'need_proxy': False
    #             }
    #         )
    #     if gfp_self_enum.SupportedWeb.Hidemy in r:
    #         self._site.append(
    #             {
    #                 # hidemy.name支持所有protocol，2种type，和国家
    #                 'urls': ['https://hidemy.name/en/proxy-list/?start=%s#list' %
    #                          str((m - 1) * 64) if m > 1 else
    #                          'https://hidemy.name/en/proxy-list/?start=1#list'
    #                          for m in range(1, self._site_max_page_no)],
    #                 'enum_site': gfp_self_enum.SupportedWeb.Hidemy,
    #                 'need_proxy': False
    #             }
    #         )


# FREE_PROXY_SITE = [
#     # {
#     #     # firefox报告安全问题
#     #     'urls': ['http://www.66ip.cn/%s.html' % n for n in
#     #              ['index'] + list(range(2, 12))],
#     #     'type': 'xpath',
#     #     'pattern': ".//*[@id='main']/div/div[1]/table/tr[position()>1]",
#     #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]',
#     #                  'protocol': ''}
#     # },
#     # {
#     #     'urls': ['http://www.66ip.cn/areaindex_%s/%s.html' % (m, n) for m in
#     #              range(1, 35) for n in range(1, 10)],
#     #     'type': 'xpath',
#     #     'pattern': ".//*[@id='footer']/div/table/tr[position()>1]",
#     #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[4]',
#     #                  'protocol': ''}
#     # },
#     # {
#     #     # 安全问题
#     #     'urls': ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218'],
#     #     'type': 'xpath',
#     #     'pattern': ".//table[@class='sortable']/tbody/tr",
#     #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
#     #                  'protocol': ''}
#     #
#     # },
#     # {
#     #     # 安全问题
#     #     'urls': ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 10)],
#     #     'type': 'xpath',
#     #     'pattern': ".//table[@class='list']/tr",
#     #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': '',
#     #                  'protocol': ''}
#     #
#     # },
#
#
#
#     # {
#     #     'urls': ['http://www.kuaidaili.com/free/%s/%s/' % (m, n) for m in
#     #              ['inha', 'intr', 'outha', 'outtr'] for n in
#     #              range(1, 11)],
#     #     'type': 'xpath',
#     #     'pattern': ".//*[@id='list']/table/tbody/tr[position()>0]",
#     #     'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]',
#     #                  'protocol': './td[4]'}
#     # },
#     {
#         'urls': ['http://www.cz88.net/proxy/%s' % m for m in
#                  ['index.shtml'] + ['http_%s.shtml' % n for n in range(2, 11)]],
#         'type': 'xpath',
#         'pattern': ".//*[@id='boxright']/div/ul/li[position()>1]",
#         'position': {'ip': './div[1]', 'port': './div[2]', 'type': './div[3]',
#                      'protocol': ''}
#
#     },
#     # firefox 警告
#     {
#         'urls': ['http://www.ip181.com/daili/%s.html' % n for n in
#                  range(1, 11)],
#         'type': 'xpath',
#         'pattern': ".//div[@class='row']/div[3]/table/tbody/tr[position()>1]",
#         'position': {'ip': './td[1]', 'port': './td[2]', 'type': './td[3]',
#                      'protocol': './td[4]'}
#
#     },
#     # {
#     #     'urls': ['http://www.xicidaili.com/%s/%s' % (m, n) for m in
#     #              ['nn', 'nt', 'wn', 'wt'] for n in range(1, 8)],
#     #     'type': 'xpath',
#     #     'pattern': ".//*[@id='ip_list']/tr[position()>1]",
#     #     'position': {'ip': './td[2]', 'port': './td[3]', 'type': './td[5]',
#     #                  'protocol': './td[6]'}
#     # },
#     {
#         'urls': ['http://www.cnproxy.com/proxy%s.html' % i for i in
#                  range(1, 11)],
#         'type': 'module',
#         'moduleName': 'CnproxyPraser',
#         'pattern': r'<tr><td>(\d+\.\d+\.\d+\.\d+)<SCRIPT type=text/javascript>document.write\(\"\:\"(.+)\)</SCRIPT></td><td>(HTTP|SOCKS4)\s*',
#         'position': {'ip': 0, 'port': 1, 'type': -1, 'protocol': 2}
#     }
# ]

if __name__ == '__main__':
    cur_setting = GfpSetting()
    print(cur_setting.proxy_type)
    # print(os.path.dirname(tempfile.gettempdir()))
    # cur_setting.site = {gfp_self_enum.SupportedWeb.Hidemy}
    # print(cur_setting.site)
    # cur_setting.site = {gfp_self_enum.SupportedWeb.Hidemy, gfp_self_enum.SupportedWeb.All}
    # print(cur_setting.site)

    # print(enum_set_check(value={gfp_self_enum.ProxyType.All},
    #                      enum_type=gfp_self_enum.ProxyType))
