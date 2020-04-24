#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# import sys
# sys.path.append('..')
from get_free_proxy.db.base import BaseDb
import get_free_proxy.self.SelfException as self_exception
# import get_free_proxy.setting.Setting as setting

import pymysql
# select返回字典而非元组
from pymysql.cursors import DictCursor
# from src import self as self_exception

import logging

import datetime

logging.basicConfig(level=logging.DEBUG)


class MySql(BaseDb):
    def __init__(self, *, host, user, pwd, port=3306, charset='utf8mb4',
                 db_name='db_proxy', tbl_name='tbl_proxy'):
        super().__init__()
        self.host = host
        self.user = user
        self.pwd = pwd
        self.port = port
        self.charset = charset
        self.db_name = db_name
        self.tbl_name = tbl_name

    def connect_to_mysql(self):

        try:
            self.conn = pymysql.connect(host=self.host, port=self.port,
                                        user=self.user,
                                        password=self.pwd, charset=self.charset)

        # Can't connect to MySQL server
        except pymysql.err.OperationalError as e:
            return False

        self.cursor = self.conn.cursor(DictCursor)
        sql = 'show databases like \'%s\'' % self.db_name
        db_exists = self.cursor.execute(sql)
        if db_exists == 1:
            self.conn.select_db(self.db_name)
        return True

    def create_db(self, *, force=False):
        super().create_db()
        sql = 'show databases like \'%s\'' % self.db_name
        db_exists = self.cursor.execute(sql)
        if db_exists == 1:
            if not force:
                logging.debug('数据库%s已经存在，无需强制创建' % self.db_name)
                return
            else:
                logging.debug('数据库%s已经存在，强制创建前先删除' % self.db_name)
                sql = 'DROP DATABASE IF EXISTS %s' % self.db_name
                self.cursor.execute(sql)

        logging.debug('开始创建数据库%s' % self.db_name)
        sql = 'CREATE DATABASE %s' % self.db_name
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            logging.error('数据库%创建失败' % self.db_name)
        logging.debug('数据库%s创建成功' % self.db_name)
        # sql = 'use %s' % self.db_name
        # self.cursor.execute(sql)
        self.conn.select_db(self.db_name)

    def create_tbl(self, *, force=False):
        super().create_tbl()
        # sql = 'use %s' % self.db_name
        # self.cursor.execute(sql)
        self.conn.select_db(self.db_name)
        sql = 'show tables like \'%s\'' % self.tbl_name
        tbl_exists = self.cursor.execute(sql)
        if tbl_exists == 1:
            if not force:
                logging.debug('表%s已经存在，无需强制创建' % self.tbl_name)
                return
            else:
                logging.debug('表%s已经存在，强制创建前先删除' % self.tbl_name)
                sql = 'DROP TABLE IF EXISTS %s' % self.tbl_name
                self.cursor.execute(sql)

        logging.debug('开始创建表%s' % self.tbl_name)
        sql = '''
        CREATE TABLE `%s` (\
`id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,\
`ip` varchar(50) NOT NULL,\
`port` varchar(50) NOT NULL,\
`proxy_type` enum('TRANS','ANON','HIGH_ANON') NOT NULL,\
`protocol` enum('HTTP','HTTPS') NOT NULL,\
`score` tinyint(3) unsigned NOT NULL DEFAULT '20',\
`ctime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,\
PRIMARY KEY (`id`),\
UNIQUE KEY `uniq` (`ip`,`port`,`proxy_type`)\
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
        ''' % self.tbl_name
        # logging.debug(sql)
        # return
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            logging.error('表%创建失败' % self.tbl_name)

        logging.debug('表%s创建成功' % self.tbl_name)

    def insert(self, gfp_setting, single_record):
        super().insert()
        # sql = 'use %s' % self.db_name
        # self.cursor.execute(sql)
        self.conn.select_db(self.db_name)
        ip = single_record['ip']
        port = single_record['port']
        proxy_type = single_record['proxy_type']
        protocol = single_record['protocol']
        due_time = datetime.datetime.now()+datetime.timedelta(seconds=gfp_setting.valid_time_in_db)
        sql = 'insert into %s(ip,port,proxy_type, protocol, due_time) values(\'%s\',\'%s\', \
              \'%s\', \'%s\', \'%s\')' % (self.tbl_name, ip, port, proxy_type, protocol, due_time)
        # logging.debug(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def insert_multi(self, gfp_setting, records=None):
        '''
        :param records: list, 元素是dict {ip:,port,proxy_type, protocol}
        :return:
        '''
        if records is None:
            return None

        if len(records) == 0:
            return None

        sql = 'insert into %s(ip,port,proxy_type, protocol, due_time) values ' % self.tbl_name
        to_be_insert_value = ''
        due_time = datetime.datetime.now() + datetime.timedelta(seconds=gfp_setting.valid_time_in_db)
        for single_record in records:
            if not self._check_insert_record(single_record):
                raise ValueError('待插入的记录格式不正确')
            else:
                # 如果已经有要插入的记录，那么先添加逗号进行分割，然后添加新的记录
                if len(to_be_insert_value) > 0:
                    to_be_insert_value += ','
                to_be_insert_value += '(\'%s\',\'%s\',\'%s\', \'%s\', \'%s\')' % (
                    single_record['ip'], single_record['port'],
                    single_record['proxy_type'], single_record['protocol'], due_time)
        sql += to_be_insert_value
        # print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def _check_insert_record(self, single_record):
        '''
        :param single_record: dict。待插入的记录，
        :return: boolean
        '''
        if len(single_record) != 4:
            raise ValueError('待插入的记录，必须包含4个字段')

        valid_record_fields = ['ip', 'port', 'proxy_type', 'protocol']
        for single_field in single_record:
            if single_field not in valid_record_fields:
                return False

        return True

    def update(self, *, condition=None, value=None):
        '''
        :param condition: None，或者字典
        :param value: None，或者字典
        :return:
        '''
        valid_fields = ['ip', 'port', 'proxy_type', 'protocol', 'score']
        if value is None:
            return

        update_value = ''
        for key in value:
            if key not in valid_fields:
                raise self_exception.InvalidFieldException(key)
            else:
                # 判断是否要添加,
                if len(update_value) > 0:
                    update_value += ','
                update_value += '%s=\'%s\'' % (key, value[key])
                # print('')

        where_condition = self._convert_condition(valid_fields=valid_fields,
                                                  condition=condition)

        sql = 'update %s set %s' % (self.tbl_name, update_value)
        if len(where_condition) > 0:
            sql += ' where %s' % where_condition
        # print(update_value)
        # print(where_condition)
        # print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def delete(self, *, condition=None):
        '''
        :param condition: None，或者字典
        :return:
        '''
        valid_fields = ['id', 'ip', 'port', 'proxy_type', 'protocol', 'score',
                        'ctime', 'due_time']

        where_condition = self._convert_condition(valid_fields=valid_fields,
                                                  condition=condition)

        sql = 'delete from %s' % self.tbl_name
        if len(where_condition) > 0:
            sql += ' where %s' % where_condition

        # print(update_value)
        # print(where_condition)
        # print(sql)
        self.cursor.execute(sql)
        self.conn.commit()

    def select(self, *, condition=None):
        '''
        :param condition: None，或者字典
        :return: 查询到的记录(tuple)或者None（没有记录）
        '''
        valid_fields = ['id', 'ip', 'port', 'proxy_type', 'protocol', 'score', 'ctime']

        where_condition = self._convert_condition(valid_fields=valid_fields,
                                                  condition=condition)
        sql = 'select ip, port, proxy_type, protocol, score, ctime from %s' % self.tbl_name
        if len(where_condition) > 0:
            sql += ' where %s' % where_condition

        result = self.cursor.execute(sql)
        if result > 0:
            self.conn.commit()
            return self.cursor.fetchall()
        return None

    def execute(self, sql):
        if 'select' in sql:
            result = self.cursor.execute(sql)
            if result > 0:
                self.conn.commit()
                return self.cursor.fetchall()
            return None
        if 'delete' in sql:
            result = self.cursor.execute(sql)
            self.conn.commit()
            return None
        if 'update' in sql:
            result = self.cursor.execute(sql)
            self.conn.commit()
            return None

    def _convert_condition(self, *, valid_fields=None, condition=None):
        '''
        valid_fields: list，where中可用的查询字段
        :param condition: None，或者字典
        :return: where string
        '''
        if valid_fields is None or len(valid_fields) == 0:
            return ''
        if condition is None:
            return ''

        where_condition = ''
        if valid_fields is not None:
            for key in condition:
                if key not in valid_fields:
                    raise self_exception.InvalidFieldException(key)
                else:
                    # 判断是否要删除 and/or/not等
                    op, value = condition[key].split(' ')
                    if len(where_condition) == 0:
                        where_condition += ' %s=\'%s\'' % (key, value)
                    else:
                        where_condition += ' %s %s=\'%s\'' % (op, key, value)
        print(where_condition)
        return where_condition


if __name__ == '__main__':
    mysql = MySql(host='127.0.0.1', user='root', pwd='1234')
    # mysql.create_db()
    # mysql.create_tbl()
    mysql.connect_to_mysql()
    # mysql.insert_multi(records=[{'ip': '1.1.1.1', 'port': '9090',
    #                              'proxy_type': self_enum.ProxyType.ANON.name, 'protocol': self_enum.ProtocolType.HTTPS.name},
    #                             {'ip': '2.2.2.2', 'port': '8080',
    #                              'proxy_type': self_enum.ProxyType.ANON.name, 'protocol': self_enum.ProtocolType.HTTPS.name}])
    # mysql.create_proc(proc_name='te', force=True)
    # mysql.update(value={'ip': '1.1.1.2'}, condition={'ip': 'and 1.1.1.1', 'port': 'or 9090'})
    #     mysql.convert_condition(valid_fields=['ip', 'port'], condition={'ip': 'and \
    # 1.1.1.1','port': 'or 9090'})
    # r=mysql.select(condition={'ip': 'and 1.1.1.1', 'port': 'or 9090'})
    r = mysql.select()
    print(r)
    # mysql.update(condition={'ip': 'and 1.1.1.1', 'port': 'or 9090'})
