#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import gevent
from gevent import monkey

# monkey.patch_all()
from requests_html import AsyncHTMLSession

asession = AsyncHTMLSession()

import random

import get_free_proxy.db.MySql as mysql
import get_free_proxy.db.Redis as redis
import get_free_proxy.db.File as file
# # print(sys.path)
# import src.setting as setting
import get_free_proxy.generator.GenProxy as gen_proxy
import get_free_proxy.helper.Checker as checker
import get_free_proxy.self.SelfEnum as gfp_self_enum
import get_free_proxy.setting.Setting as gfp_setting
import get_free_proxy.self.EnumMatchInst as gfp_enum_match_inst

import gen_browser_header.helper.Helper as gbh_helper
import gen_browser_header.main.GenHeader as gen_header
import gen_browser_header.setting.Setting as gbh_setting


class MainOp(object):
    __slots__ = ('_setting', '_gbh_setting', '_site',
                 '_mysql_inst', '_redis_inst', '_file_inst', '_assesion_inst')

    def __init__(self, setting, gbh_setting):
        self._setting = setting
        self._gbh_setting = gbh_setting
        # 因为要检测site是否需要代理，并存储结果；而setting.site不是直接
        # 保存 所赋的值（会将enum转换成dict），所以需要一个setting.site的副本
        self._site = self._setting.site.copy()
        if gfp_self_enum.StorageType.Mysql in self._setting.storage_type:

            if not checker.win_check_mysql_running():
                checker.win_start_mysql()
            if not self._mysql_inst.connect_to_mysql():
                raise Exception('can not connect to mysql, please check if service Mysql already run')
            # 初始化mysql实例
            self._mysql_inst = mysql.MySql(host=setting.mysql['host'],
                                           user=setting.mysql['user'],
                                           pwd=setting.mysql['pwd'])
            self._mysql_inst.create_db()
            self._mysql_inst.create_tbl()
        else:
            self._mysql_inst = None

        if gfp_self_enum.StorageType.Redis in self._setting.storage_type:
            # 初始化redis实例
            self._redis_inst = redis.Redis(host=setting.redis['host'],
                                           # user=setting.STOREAGE[db_type]['user'],
                                           pwd=setting.redis['pwd'],
                                           port=setting.redis['port']
                                           )
            self._redis_inst.connect_to_redis()
        else:
            self._redis_inst = None

        if gfp_self_enum.StorageType.File in self._setting.storage_type:
            self._file_inst = self._setting.result_file_path
        else:
            self._file_inst = None

        self._assesion_inst = AsyncHTMLSession()

    @property
    def setting(self):
        return self._setting

    @setting.setter
    def setting(self, value):
        self._setting = value

    @property
    def gbh_setting(self):
        return self._gbh_setting

    @gbh_setting.setter
    def gbh_setting(self, value):
        self._gbh_setting = value

    @property
    def site(self):
        return self._site

    @property
    def mysql_inst(self):
        return self._mysql_inst

    @property
    def redis_inst(self):
        return self._redis_inst

    @property
    def file_inst(self):
        return self._file_inst

    @property
    def asession_inst(self):
        return self._asession_inst

    def check_if_site_need_proxy(self):
        # print(self._site)
        for single_site in self._site:
            single_site['need_proxy'] = gbh_helper.detect_if_need_proxy(single_site['urls'][0])
        # print(self._site)

    def get_proxy_without_proxy(self):
        '''
        从网站获得代理
        :return:
        '''
        origin_result = []
        for single_site in self._site:
            # print(single_site['need_proxy'])
            # print(single_site)
            if not single_site['need_proxy']:
                url_num = len(single_site['urls'])
                if url_num > 0:
                    generated_headers = gen_header.gen_header(setting=self._gbh_setting,
                                                              url=single_site['urls'][0],
                                                              num=url_num)
                    # print(generated_headers)

                    origin_result += gen_proxy.gen_proxy_async(enum_site=single_site['enum_site'],
                                                               sites=single_site,
                                                               gfp_setting=self._setting,
                                                               headers=generated_headers,
                                                               proxies=None)
                # r = gen_proxy.gen_proxy_async(asession_inst=asession, enum_site=gfp_self_enum.SupportedWeb.Xici,
                #                               sites={'urls': ['https://www.baidu.com']},
                #                               gfp_setting={},
                #                               headers=[],
                #                               proxies=[])
        return origin_result
        # print(origin_result)

        # self.redis.bf_create()
        # self.redis.bf_madd(records=origin_result)

    def get_proxy_with_proxy(self, proxies=None):
        '''
        从网站获得代理
        :param proxies: list，所有从get_proxy_without_proxy且经过验证的proxy
        :return:
        '''
        if proxies is None or len(proxies) == 0:
            # print(self._gbh_setting.proxy_ip)
            if self._gbh_setting.proxy_ip is None:
                raise ValueError('对需要代理的url进行处理时，没有任何可用的代理')
            else:
                proxies = self._gbh_setting.proxies
        # print('proxy_ip is:')
        # print(self._gbh_setting.proxy_ip)
        # print('self._site %s' % self._site)
        origin_result = []
        # final_result = []
        for single_site in self._site:
            if single_site['need_proxy']:
                url_num = len(single_site['urls'])

                if url_num > 0:
                    generated_headers = gen_header.gen_header(setting=self._gbh_setting,
                                                              url=single_site['urls'][0],
                                                              num=url_num)
                    # print(generated_headers)
                    if url_num > len(proxies):
                        to_be_used_proxies = proxies
                    else:
                        to_be_used_proxies = random.sample(proxies, url_num)

                    origin_result += gen_proxy.gen_proxy_async(enum_site=single_site['enum_site'],
                                                               sites=single_site, gfp_setting=self._setting,
                                                               headers=generated_headers,
                                                               proxies=to_be_used_proxies,
                                                               force_render=single_site['force_render'])

                # extract_data_function = gfp_enum_match_inst.getExtractDataFunction(single_site['enum_site'])
                # # logging.info('extract_data_function is %s' % extract_data_function)
                # if extract_data_function is None:
                #     raise ValueError('无法根据网站名称%s找到对应的extract_data函数' % single_site['enum_site'].name)
                #
                # for single_raw_result in origin_raw_result:
                #     final_result += extract_data_function(single_raw_result, gfp_setting)
        return origin_result

    def validate_single_proxy(self, single_proxy, url, final_result):
        '''
        :param single_proxy:dict。 gen_proxy获得的结果中，单个记录。{ip,port,type,protocol}
        :param url: 代理对此url是否有效
        :param final_result:list。为了在协程中直接将valid的proxy提取，直接传入此参数
        :return: boolean。实际上，使用协程时，无法使用此返回值，而是直接将结果放入final_result
        '''
        ip = single_proxy['ip']
        port = single_proxy['port']
        proxy = {
            'http': '%s:%s' % (ip, port),
            'https': '%s:%s' % (ip, port)
        }
        print('开始检测代理%s:%s对网站%s是否有效' % (single_proxy['ip'],single_proxy['port'], url))
        # print(proxy)
        if gbh_helper.detect_if_proxy_usable(proxies=proxy, url=url):
            print('代理 %s 有效' % proxy['http'])
            final_result.append(single_proxy)
            return True
        else:
            print('代理 %s 无效' % proxy['http'])
            # final_result.append(single_result)
            return False

    def async_validate_proxies(self, proxies, url):
        '''
        :param proxies: list。 页面中获得的代理，需要进行检测，是否valid
        :return: list(final_result)
        '''
        if len(proxies) == 0:
            return proxies
        monkey.patch_all()
        task_list = []
        # logging.debug(psutil.cpu_count())
        # print(proxies)
        # p = Pool(2)
        final_result = []
        # if len(result) > 10:
        #     headers = gen_header.gen_limit_header(len(result))
        # else:
        #     headers = gen_header.gen_limit_header(1)

        for single_proxy in proxies:
            # header = random.choice(proxies)
            task_list.append(
                gevent.spawn(self.validate_single_proxy, single_proxy,
                             url, final_result)
            )
            # p.apply_async(check_proxies_validate, args=(single_proxy,))
        # p.apply_async(check_proxies_validate, args=(proxies[1],))
        # print('Waiting for gevent done...')
        # start_time = time.time()
        gevent.joinall(task_list)
        # end_time = time.time()
        # print('All gevent done. total cost %s ms' % (end_time - start_time))
        # print(final_result)
        return final_result

    def _add_score_for_redis(self, proxies):
        for single_proxy in proxies:
            single_proxy['score'] = 20

    def save_proxy(self, proxies):
        # print(len(proxies))
        # print(self._setting.storage_type)
        if len(proxies) > 0:
            if gfp_self_enum.StorageType.Mysql in self._setting.storage_type:
                print('start to save proxies into mysql')
                self._mysql_inst.insert_multi(gfp_setting=self.setting, records=proxies)
            if gfp_self_enum.StorageType.File in self._setting.storage_type:
                print('start to save proxies into redis')
                file.save_proxies(self._file_inst, proxies)
            if gfp_self_enum.StorageType.Redis in self._setting.storage_type:
                print('start to save proxies into file')
                self._add_score_for_redis(proxies=proxies)
                self._redis_inst.multi_hmet(records=proxies, validate_time=self.setting.valid_time_in_db)

    def pickup_proxy_ip(self, num):
        # 尽量选择较少使用的proxy
        sql = 'select id, ip, port, proxy_type, protocol from tbl_proxy where score > 0 and due_time > now()  \
              order by score desc, due_time limit %s' % num
        result = self._mysql_inst.execute(sql)
        return result

    def reduce_score(self, records):
        id_list = [str(item['id']) for item in records]
        # print(','.join(id_list))
        # print(type(','.join(id_list)))
        sql = 'update tbl_proxy set score=score-1 where id in (%s)' % ','.join(id_list)
        # print(sql)
        self._mysql_inst.execute(sql)
        # return id_list

    def del_proxy(self):
        '''
        因为布隆过滤器无法删除item，且读取网页会读取所有记录（而不是选择性的读取），所以干脆全部删除，在重新写入db
        :return:
        '''
        if self._mysql_inst is not None:
            sql = 'delete from tbl_proxy'
            self._mysql_inst.execute(sql)
        if self._redis_inst is not None:
            # redis中删除所有key
            self._redis_inst.delete_all()
        if self._file_inst is not None:
            # 文件清空
            with open(self._file_inst,'w') as f:
                f.truncate()

if __name__ == '__main__':
    import gen_browser_header.self.SelfEnum as gbh_self_enum

    import os
    import tempfile

    import logging

    logging.basicConfig(level=logging.INFO)
    cur_gbh_setting = gbh_setting.GbhSetting()
    cur_gbh_setting.proxy_ip = ['87.254.212.121:8080']
    cur_gbh_setting.browser_type = {gbh_self_enum.BrowserType.All}
    cur_gbh_setting.firefox_ver = {'min': 74, 'max': 75}
    cur_gbh_setting.chrome_type = {gbh_self_enum.ChromeType.Stable}
    cur_gbh_setting.chrome_max_release_year = 1
    cur_gbh_setting.os_type = {gbh_self_enum.OsType.Win64}

    cur_gfp_setting = gfp_setting.GfpSetting()
    cur_gfp_setting.raw_site = {gfp_self_enum.SupportedWeb.Xici}
    cur_gfp_setting.proxy_type = {gfp_self_enum.ProxyType.HIGH_ANON}
    cur_gfp_setting.protocol = {gfp_self_enum.ProtocolType.HTTP,
                                # gfp_self_enum.ProtocolType.HTTPS
                                }
    cur_gfp_setting.country = {gfp_self_enum.Country.All}
    cur_gfp_setting.storage_type = {gfp_self_enum.StorageType.File}
    cur_gfp_setting.mysql = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'pwd': '1234',
        'db_name': 'db_proxy',
        'tbl_name': 'tbl_proxy',
        'charset': 'utf8mb4'
    }
    cur_gfp_setting.redis = {
        'host': '127.0.0.1',
        'port': 6379,
        'db': 0,  # 0~15
        'pwd': None
    }
    cur_gfp_setting.result_file_path = os.path.join(tempfile.gettempdir(), 'result.json')
    # print(tempfile.gettempdir())
    cur_gfp_setting.valid_time_in_db = 86400
    cur_gfp_setting.site_max_page_no = 1

    # print(cur_gfp_setting.site)

    mainOp = MainOp(cur_gfp_setting, cur_gbh_setting)
    # 首先清空数据库(反正都要全部重新读取网页）
    mainOp.del_proxy()
    # print('delete proxy done')
    # 检测url是否需要使用代理
    mainOp.check_if_site_need_proxy()
    # print('check_if_site_need_proxy done')
    # 获得代理
    tmp_proxies = mainOp.get_proxy_without_proxy()
    # print('get proxy no proxy done')
    # print(tmp_proxies)
    # logging.info('tmp_proxies is %s' % str(tmp_proxies))
    first_validate_proxies = mainOp.async_validate_proxies(tmp_proxies, 'https://www.baidu.com')
    # logging.info('first_validate_proxies is %s' % str(first_validate_proxies))
    if len(first_validate_proxies) > 0:
        tmp_proxies = mainOp.get_proxy_with_proxy(proxies=first_validate_proxies)
    else:
        tmp_proxies = mainOp.get_proxy_with_proxy(proxies=None)

    second_validate_proxies = mainOp.async_validate_proxies(tmp_proxies, 'https://www.baidu.com')

    all_validate_proxies = first_validate_proxies+second_validate_proxies
    print('最终有效代理%s' % all_validate_proxies)
    mainOp.save_proxy(proxies=all_validate_proxies)
    # print('save proxy done')
    # return tmp_proxies
    # print(first_validate_proxies+second_validate_proxies)
    # result = mainOp.pickup_proxy_ip(num=5)
    # mainOp.reduce_score(records=result)
    # mainOp.pickup_proxy_ip(num=2)
