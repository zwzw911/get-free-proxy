#! /usr/bin/env python3
# -*- coding:utf-8 -*-
from get_free_proxy.db.base import BaseDb
import gen_browser_header.helper.Helper as helper
from get_free_proxy.self.SelfException import InvalidFieldException

# redis用来捕获错误
import redis
# 使用redisbloom代替redis：redisbloom继承redis，且有bloom功能
from redisbloom.client import Client


import datetime


class Redis(BaseDb):
    '''
    proxy以 proxy:IP:port作为key，以hash方式存储，field为type, protocol,score, ctime
    '''

    __slots__ = ('_filter_name')

    @property
    def filter_name(self):
        return self._filter_name

    @filter_name.setter
    def filter_name(self, value):
        self._filter_name = value

    def __init__(self, host, pwd=None, port=6379, db=0):
        super().__init__()
        self.host = host
        self.pwd = pwd
        self.port = port
        self.db = db
        self._filter_name = ''

    def connect_to_redis(self):
        try:
            self.conn = Client(host=self.host, port=self.port,
                               db=self.db, password=self.pwd)
        except Exception as e:
            print(e)
            return False

        return True

    def gen_key_name(self, record):
        # print(record)
        # print('ip' in record)
        # print('port' in record)
        if 'ip' in record and 'port' in record:
            return 'Proxy:%s:%s' % (record['ip'], record['port'])
        else:
            return None

    def exists(self, key_name):
        '''
        判断key是否已经存在，普通方式，和bf做对比，实际不使用
        :param key_name:
        :return: 0（false）/1（True）
        '''
        return self.conn.exists(key_name)

    def delete(self, key_name):
        return self.conn.delete(key_name)

    def delete_all(self):
        return self.conn.flushdb()
    # def hdelete(self, key_name):
    #     return self.conn.hdel(key_name)

    def hmset(self, record, validate_time):
        valid_fields = ['ip', 'port', 'proxy_type', 'protocol', 'score']
        # print(record)
        for single_valid_field in valid_fields:
            # print(single_valid_field)
            # print(single_valid_field not in record)
            if single_valid_field not in record:
                raise InvalidFieldException(single_valid_field)

        key_name = self.gen_key_name(record)
        field_value = {
            'proxy_type': record['proxy_type'],
            'protocol': record['protocol'],
            'score': record['score'],
            # 'ctime': record['ctime']
        }

        self.conn.hmset(key_name, field_value)
        self.conn.expire(key_name, validate_time)

    def multi_hmet(self, records, validate_time):
        for single_record in records:
            # print(single_record)
            self.hmset(single_record, validate_time)


    def time_interval_in_seconds(self, old_date_time, new_date_time):
        '''
        计算old_date_time和new_date_time之间时间间隔，单位秒
        :param old_date_time:
        :param new_date_time:
        :return:    int
        '''

        if not helper.match_expect_type(old_date_time, 'datetime.datetime'):
            if helper.match_expect_type(old_date_time, 'str'):
                old_date_time = datetime.datetime.strptime(old_date_time, '%Y-%m-%d %H:%M:%S')
            else:
                raise ValueError('old_date_time的格式不正确')

        if not helper.match_expect_type(new_date_time, 'datetime.datetime'):
            if helper.match_expect_type(new_date_time, 'str'):
                new_date_time = datetime.datetime.strptime(new_date_time, '%Y-%m-%d %H:%M:%S')
            else:
                raise ValueError('new_date_time的格式不正确')

        # datetime.datetime.now()+datetime.timedelta(days=1)
        return int((new_date_time - old_date_time).total_seconds())
        # print((new_date_time - old_date_time).total_seconds())

    def expire(self, key_name, ttl):
        return self.conn.expire(key_name, ttl)

    def bf_create(self, fpp=0.001, capacity=1000, expansion=1):
        '''
        创建一个bloom过滤器
        :param filter_name: 过滤器名称
        :param fpp: 假阳性概率
        :param capacity: 过滤器存储元素的个数
        :param expansion: 当filter填满后，新建的子filter的capacity是当前filter的几倍大小。1，说明同样大小
        :return: 0(create fail)/1(create success)
        '''
        try:
            self.conn.bfCreate(key=self._filter_name, errorRate=fpp, capacity=capacity, expansion=expansion)
        except redis.exceptions.ResponseError as e:
            # print(e)    #item exists
            return 0
        return 1

    def bf_madd(self, records):
        items = ''
        for single_record in records:
            items += self.gen_key_name(single_record)
        self.conn.bfMAdd(self._filter_name, items)

    def bf_add(self, record):
        item = self.gen_key_name(record)

        self.conn.bfMAdd(self._filter_name, item)

    def bf_exists(self, item):
        return self.conn.bfExists(self._filter_name, item)

    def bf_mexists(self, items):
        '''
        :param items: 是一个list，调用bfMExists，加*变成可变参数
        :return:
        '''
        return self.conn.bfMExists(self._filter_name, *items)


if __name__ == '__main__':
    import sys
    print(sys.path)
    r = Redis('127.0.0.1')
    r.filter_name='bf_proxy'
    # print(r.filter_name)
    r.connect_to_redis()
    # print(r.exists(key_name=bf_key_name))
    if r.exists(r.filter_name):
        # print('bf_key_name exists')
        r.delete(r.filter_name)
    r.bf_create(fpp=0.001, capacity=1000)
    records = [{'ip': '1.1.1.1', 'port': '9090', 'proxy_type': 'ANON', 'protocol': 'HTTPS', 'score': 20,
                'ctime': datetime.datetime(2020, 4, 10, 16, 18, 33)}]
    for single_record in records:
        key_name = r.gen_key_name(single_record)
        if key_name is not None:
            ttl = r.time_interval_in_seconds(single_record['ctime'], datetime.datetime.now())
            # print(ttl)
            r.hmset(single_record)
            r.expire(key_name, ttl)

    r.bf_madd(records)
    result = r.bf_exists(r.gen_key_name(records[0]))
    print(result)
    l = [r.gen_key_name(records[0])]
    print(l)
    result = r.bf_mexists(l)
    print(result)
    # print(r.bf_exists('not exists'))
    # r.bf_create(bf_key_name, 0.001, 1)
